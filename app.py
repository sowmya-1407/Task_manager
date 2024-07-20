


import re
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import datetime
import jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Sowmya_14',  # Replace with your password
    'database': 'task_manage2_db'
}


def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as e:
        print("Error connecting to MySQL:", e)
        return None
    
#photo code settings

ITEMS_PER_PAGE = 4
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn is None:
            msg = 'Could not connect to the database'
            return render_template('login.html', msg=msg)
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        users = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if users:
            session['loggedin'] = True
            session['user_id'] = users['user_id']
            session['username'] = users['username']
            msg = 'Logged in successfully!'
            return render_template('website.html', msg=msg)
        else:
            msg = 'Incorrect username / password!'
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            conn = get_db_connection()
            if conn is None:
                msg = 'Could not connect to the database'
                return render_template('register.html', msg=msg)
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            account = cursor.fetchone()
            
            if account:
                msg = 'Account already exists!'
            else:
                cursor.execute('INSERT INTO users (username, password, email) VALUES (%s, %s, %s)', (username, password, email,))
                conn.commit()
                msg = 'You have successfully registered!'
            
            cursor.close()
            conn.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/website')
def website():
    return render_template('website.html')

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT COUNT(*) AS count FROM tasks")
            tasks_count = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) AS count FROM categories")
            categories_count = cursor.fetchone()['count']

            # cursor.execute("SELECT COUNT(*) AS count FROM tasks")
            # priorities_count = cursor.fetchone()['count']

            # cursor.execute("SELECT COUNT(*) AS count FROM tasks")
            # due_dates_count = cursor.fetchone()['count']
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            tasks_count = categories_count  = 0
        finally:
            cursor.close()
            connection.close()
        
        return render_template('dashboard.html', tasks_count=tasks_count, categories_count=categories_count )
    else:
        return redirect(url_for('login'))



@app.route('/create_task', methods=['GET', 'POST'])
def create_task():
    conn = get_db_connection()
    if conn is None:
        flash('Could not connect to the database')
        return redirect(url_for('dashboard'))

    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        user_id = session['user_id']
        task_title = request.form['task_title']
        description = request.form['description']
        category_id = request.form['category_id']
        # title = request.form['title']
        priority = request.form['priority']
        due_date = request.form['due_date']
        
        cursor.execute("""
            INSERT INTO tasks (user_id, task_title, description, category_id, priority, due_date)
            VALUES (%s, %s, %s, %s, %s,  %s)
        """, (user_id, task_title, description, category_id, priority, due_date))
        
        conn.commit()
        flash('Task created successfully!')
        return redirect(url_for('view_tasks'))
    
    cursor.execute('SELECT * FROM categories')
    categories = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('create_task.html', categories=categories)




@app.route('/user_view_tasks')
def user_view_tasks():
    if 'loggedin' in session:
        conn = get_db_connection()
        if conn is None:
            flash('Could not connect to the database')
            return render_template('user_view_tasks.html', data=[])
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tasks")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return render_template('user_view_tasks.html', data=data)
    else:
        return redirect(url_for('login'))




@app.route('/view_tasks')
def view_tasks():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    if conn is None:
        flash('Could not connect to the database')
        return render_template('view_tasks.html', data=[])

    cursor = conn.cursor(dictionary=True)

    # Fetch total number of items
    cursor.execute('SELECT COUNT(*) AS count FROM tasks WHERE user_id = %s', (user_id,))
    total_items = cursor.fetchone()['count']
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    # Get the current page number from the query parameter, default to 1
    page = int(request.args.get('page', 1))
    offset = (page - 1) * ITEMS_PER_PAGE

    # Fetch tasks for the current page
    query = '''
        SELECT tasks.task_id, tasks.task_title, tasks.description, categories.title as category, 
               tasks.priority, tasks.due_date, tasks.created_at, tasks.updated_at
        FROM tasks
        LEFT JOIN categories ON tasks.category_id = categories.category_id
        WHERE tasks.user_id = %s
        LIMIT %s OFFSET %s
    '''
    cursor.execute(query, (user_id, ITEMS_PER_PAGE, offset))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_tasks.html', data=data, page=page, total_pages=total_pages)




app.route('/create_category', methods=['POST'])
def create_category():
    category_name = request.form['category']
    
    conn = get_db_connection()
    if conn is None:
        flash('Could not connect to the database')
        return redirect(url_for('create_category'))
    
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categories WHERE title = %s', (category_name,))
    existing_category = cursor.fetchone()
    
    if existing_category:
        flash('Category already exists!', 'error')
    else:
        cursor.execute('INSERT INTO categories (title) VALUES (%s)', (category_name,))
        conn.commit()
        flash('Category added successfully!', 'success')
    
    cursor.close()
    conn.close()
    
    return redirect(url_for('view_categories'))



@app.route('/delete_story/<int:task_id>', methods=['POST'])
def delete_story(task_id):
    user_id = session['user_id']
    
    conn = get_db_connection()
    if conn is None:
        flash('Could not connect to the database')
        return redirect(url_for('view_tasks'))
    
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE task_id = %s AND user_id = %s', (task_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Task deleted successfully')
    return redirect(url_for('view_tasks'))



@app.route("/update/<task_id>", methods=['POST', 'GET'])
def update(task_id):
    conn = get_db_connection()
    if conn is None:
        flash('Could not connect to the database')
        return redirect(url_for('view_tasks'))
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE task_id = %s", (task_id,))
    value = cursor.fetchone()
    
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('edit_task.html', data=value, categories=categories)

@app.route('/edit_task', methods=['POST'])
def edit_task():
    if request.method == 'POST':
        task_id = request.form['task_id']
        task_title = request.form['task_title']
        description = request.form['description']
        category_id = request.form['category_id']
        priority = request.form['priority']
        due_date = request.form['due_date']
        
        conn = get_db_connection()
        if conn is None:
            flash('Could not connect to the database')
            return redirect(url_for('view_tasks'))
        
        cursor = conn.cursor()
        try:
            update_query = '''UPDATE tasks SET task_title = %s, description = %s, category_id = %s, priority = %s, due_date = %s WHERE task_id = %s'''
            cursor.execute(update_query, (task_title, description, category_id, priority, due_date, task_id))
            conn.commit()
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('view_tasks'))
    else:
        return redirect(url_for('dashboard'))





@app.route('/view_category', methods=['GET', 'POST'])
def view_category():
    conn = get_db_connection()
    if conn is None:
        flash('Could not connect to the database')
        return render_template('view_category.html', tasks=[], categories=[])

    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        category_id = request.form['category_id']
        cursor.execute('SELECT * FROM tasks WHERE category_id = %s AND user_id = %s', (category_id, session['user_id']))
        tasks = cursor.fetchall()
    else:
        tasks = []

    cursor.execute('SELECT * FROM categories')
    categories = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_category.html', tasks=tasks, categories=categories)



@app.route('/view_priority', methods=['GET', 'POST'])
def view_priority():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn is None:
        flash('Could not connect to the database')
        return render_template('view_priority.html', tasks=[])

    cursor = conn.cursor(dictionary=True)

    tasks = []
    if request.method == 'POST':
        priority = request.form['priority']
        cursor.execute(
            'SELECT * FROM tasks WHERE priority = %s AND user_id = %s', 
            (priority, session['user_id'])
        )
        tasks = cursor.fetchall()

    priorities = ['low', 'medium', 'high']

    cursor.close()
    conn.close()

    return render_template('view_priority.html', tasks=tasks, priorities=priorities)




@app.route('/view_categories')
def view_categories():
    conn = get_db_connection()
    if conn is None:
        flash('Could not connect to the database')
        return render_template('view_categories.html', categories=[])

    try:
        page = int(request.args.get('page', 1))
        offset = (page - 1) * ITEMS_PER_PAGE

        cursor = conn.cursor(dictionary=True)

        # Fetch total number of items
        cursor.execute('SELECT COUNT(*) AS count FROM categories')
        total_items = cursor.fetchone()['count']
        total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

        # Fetch categories for the current page
        cursor.execute('SELECT category_id, title FROM categories LIMIT %s OFFSET %s', (ITEMS_PER_PAGE, offset))
        categories = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('view_categories.html', categories=categories, page=page, total_pages=total_pages)

    except mysql.connector.Error as e:
        flash(f'Error fetching categories: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))




@app.route('/create_category', methods=['GET', 'POST'])
def create_category():
    if request.method == 'POST':
        category_name = request.form['category_name']
        if not category_name:
            flash('Category name is required!', 'danger')
            return redirect(url_for('view_categories'))
        
        conn = get_db_connection()
        if conn is None:
            flash('Could not connect to the database')
            return redirect(url_for('view_categories'))
        
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categories WHERE title = %s', (category_name,))
        existing_category = cursor.fetchone()
        
        if existing_category:
            flash('Category already exists!', 'error')
        else:
            cursor.execute('INSERT INTO categories (title) VALUES (%s)', (category_name,))
            conn.commit()
            flash('Category added successfully!', 'success')
        
        cursor.close()
        conn.close()
    
    return redirect(url_for('view_categories'))





@app.route('/view_due_dates')
def view_due_dates():
    conn = get_db_connection()
    if conn is None:
        flash('Could not connect to the database')
        return render_template('view_due_dates.html', tasks=[])
    
    page = int(request.args.get('page', 1))
    offset = (page - 1) * ITEMS_PER_PAGE
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT COUNT(*) AS total FROM tasks WHERE user_id = %s', (session['user_id'],))
    total_items = cursor.fetchone()['total']
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    cursor.execute('SELECT task_title, description, due_date FROM tasks WHERE user_id = %s ORDER BY due_date ASC LIMIT %s OFFSET %s', 
                   (session['user_id'], ITEMS_PER_PAGE, offset))
    tasks = cursor.fetchall()
    
    cursor.close()
    conn.close()

    current_date = datetime.date.today()
    return render_template('view_due_dates.html', tasks=tasks, current_date=current_date, page=page, total_pages=total_pages)





@app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    conn = get_db_connection()
    if conn is None:
        flash('Could not connect to the database')
        return redirect(url_for('view_categories'))
    
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        new_title = request.form['category']
        try:
            cursor.execute("UPDATE categories SET title = %s WHERE category_id = %s", (new_title, category_id))
            conn.commit()
            flash('Category updated successfully!', 'success')
        except mysql.connector.Error as e:
            flash(f'Error updating category: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('view_categories'))
    else:
        cursor.execute("SELECT * FROM categories WHERE category_id = %s", (category_id,))
        category = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit_category.html', category=category)


@app.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    conn = get_db_connection()
    if conn is None:
        flash('Could not connect to the database')
        return redirect(url_for('view_categories'))

    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM categories WHERE category_id = %s', (category_id,))
        conn.commit()
        flash('Category deleted successfully.', 'success')
    except mysql.connector.Error as e:
        flash(f'Error deleting category: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_categories'))


@app.route('/view_desc/<int:task_id>', methods=['POST', 'GET'])
def view_desc(task_id):
    if 'loggedin' in session:
        conn = get_db_connection()
        if conn is None:
            flash('Could not connect to the database')
            return redirect(url_for('dashboard'))
        
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT task_title, description FROM tasks WHERE task_id = %s AND user_id = %s", (task_id, session['user_id']))
            task_data = cursor.fetchone()
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            task_data = None
        finally:
            cursor.close()
            conn.close()
        
        if task_data:
            return render_template('view_desc.html', task_data=task_data)
        else:
            flash('Task not found', 'error')
            return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))





import os







app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
#photo code ends


@app.route('/edit_account', methods=['GET', 'POST'])
def edit_account():
    if 'user_id' not in session:
        flash('You need to be logged in to edit your account')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Establish a database connection
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        
        if 'profile_pic' in request.files:
            profile_pic = request.files['profile_pic']
            if profile_pic and allowed_file(profile_pic.filename):
                profile_pic_filename = secure_filename(profile_pic.filename)
                
                # Create the directory if it does not exist
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                
                profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_pic_filename))
                
                # Update the user's profile pic in the database
                cursor.execute('''
                    UPDATE users
                    SET username = %s, email = %s, profile_pic = %s
                    WHERE user_id = %s
                ''', (username, email, profile_pic_filename, user_id))
            else:
                cursor.execute('''
                    UPDATE users
                    SET username = %s, email = %s
                    WHERE user_id = %s
                ''', (username, email, user_id))
        else:
            cursor.execute('''
                UPDATE users
                SET username = %s, email = %s
                WHERE user_id = %s
            ''', (username, email, user_id))
        
        conn.commit()
        flash('Account updated successfully')
        return redirect(url_for('edit_account'))
    
    cursor.execute('SELECT username, email, profile_pic FROM users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('edit_account.html', user=user)

# @app.route('/profile')
# def profile():
#     if 'user_id' not in session:
#         flash('You need to be logged in to view your profile')
#         return redirect(url_for('login'))
    
#     user_id = session['user_id']
    
#     # Establish a database connection
#     conn = mysql.connector.connect(**db_config)
#     cursor = conn.cursor(dictionary=True)
    
#     # Retrieve user information from the database
#     cursor.execute('SELECT username, email, profile_pic FROM users WHERE user_id = %s', (user_id,))
#     user = cursor.fetchone()
    
#     cursor.close()
#     conn.close()
    
#     if not user:
#         flash('User not found')
#         return redirect(url_for('login'))
    
#     return render_template('profile.html', user=user)
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('You need to be logged in to view your profile')
        return redirect(url_for('login'))
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    user_id = session['user_id']
    cursor.execute('SELECT username, email, profile_pic FROM users WHERE user_id = %s', (user_id,))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if request.method == 'POST':
        if 'profile_pic' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['profile_pic']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploads_dir = os.path.join(app.root_path, 'static/uploads')

            os.makedirs(uploads_dir, exist_ok=True)
            photo_path = os.path.join(uploads_dir, filename)
            file.save(photo_path)
            user_id = session['user_id']
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET profile_pic = %s WHERE user_id = %s', (filename, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Profile picture uploaded successfully!')
            return redirect(url_for('profile'))
            
    return render_template('profile.html', user=user)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
#photo code ends


@app.route('/upload_profile', methods=['GET', 'POST'])
def upload_profile():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'profile_pic' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['profile_pic']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploads_dir = os.path.join(app.root_path, 'static/uploads')

            os.makedirs(uploads_dir, exist_ok=True)
            photo_path = os.path.join(uploads_dir, filename)
            file.save(photo_path)
            user_id = session['user_id']
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET profile_pic = %s WHERE user_id = %s', (filename, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Profile picture uploaded successfully!')
            return redirect(url_for('edit_account'))

        flash('File type not allowed')
        return redirect(request.url)

    return render_template('upload_profile.html')

@app.route('/profiles')
def profiles():
    if 'loggedin' in session:
        user_id = session['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT username, email, profile_pic FROM users WHERE user_id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return render_template('profiles.html', user=user)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)