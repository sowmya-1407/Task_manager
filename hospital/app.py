from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your secret key'

try:
    conn = mysql.connector.connect(
        host='localhost',
        user="root",
        password='Sowmya_14',
        database='hospital_db'
    )
    cursor = conn.cursor()
except mysql.connector.Error as e:
    print("Error connecting to MySQL database:", e)

# Route for the home page (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Route for the about us page (about_us.html)
@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

# Route for the service page (service.html)
@app.route('/service')
def service():
    return render_template('service.html')

# Route for the doctors page (doctors.html)
@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

# Route for the contact us page (contact_us.html)
@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')

# @app.route("/appointment", methods=['GET', 'POST'])
# def appointment():
#     msg = ''
#     if request.method == 'POST' and all(k in request.form for k in ['ID' 'fname', 'lname', 'email', 'mobile', 'sex', 'appointment', 'description']):
#         ID=request.form['ID']
#         fname = request.form['fname']
#         lname = request.form['lname']
#         email = request.form['email']
#         mobile = request.form['mobile']
#         sex = request.form['sex']
#         appointment = request.form['appointment']
#         description = request.form['description']

#         try:
#             cursor.execute("INSERT INTO appointment (ID, fname, lname, email, mobile, sex, appointment, description) VALUES (%s, %s, %s, %s, %s, %s, %s)",
#                            (ID, fname, lname, email, mobile, sex, appointment, description))
            
#             data=cursor.fetchall()
#             conn.commit()
#             return redirect("dashboard.html", data=data)
            
#             msg = 'You have successfully added an appointment!'
#         except mysql.connector.Error as e:
#             print("Error executing SQL query:", e)
#             msg = 'An error occurred. Please try again later.'

#         return redirect(url_for('dashboard'))
    
#     return render_template('dashboard.html', msg=msg)
# @app.route("/dashboard")
# def dashboard():
#     try:
#         cursor.execute('SELECT * FROM appointment')
#         data = cursor.fetchall()
#         return render_template("dashboard.html", data=data)
#     except mysql.connector.Error as e:
#         print("Error executing SQL query:", e)
#         return "An error occurred. Please try again later."

# @app.route('/update/<int:ID>', methods=['GET', 'POST'])
# def update(ID):
#     msg = ''
#     if request.method == 'POST' and all(k in request.form for k in ['Firstname', 'Lastname', 'Email', 'Mobile_number', 'Sex', 'appointment_date', 'description']):
#         Firstname = request.form['Firstname']
#         Lastname = request.form['Lastname']
#         Email = request.form['Email']
#         Mobile_number = request.form['Mobile_number']
#         Sex = request.form['Sex']
#         appointment_date = request.form['appointment_date']
#         description = request.form['description']

#         try:
#             cursor.execute(
#                 'UPDATE appointment SET Firstname = %s, Lastname = %s, Email = %s, Mobile_number = %s, Sex = %s, appointment_date = %s, description = %s WHERE ID = %s',
#                 (Firstname, Lastname, Email, Mobile_number, Sex, appointment_date, description, ID)
#             )
#             conn.commit()
#             msg = 'Appointment updated successfully!'
#         except mysql.connector.Error as e:
#             print("Error executing SQL query:", e)
#             msg = 'An error occurred. Please try again later.'

#         return redirect(url_for('dashboard'))

#     try:
#         cursor.execute('SELECT * FROM appointment WHERE ID = %s', (ID,))
#         appointment = cursor.fetchone()
#         if appointment:
#             return render_template('update.html', appointment=appointment)
#         else:
#             return "Appointment not found"
#     except mysql.connector.Error as e:
#         print("Error executing SQL query:", e)
#         return "An error occurred. Please try again later."

# # Route to delete an appointment
# @app.route('/delete/<int:ID>')
# def delete(ID):
#     try:
#         cursor.execute('DELETE FROM appointment WHERE ID = %s', (ID,))
#         conn.commit()
#         msg = 'Appointment deleted successfully!'
#     except mysql.connector.Error as e:
#         print("Error executing SQL query:", e)
#         msg = 'An error occurred. Please try again later.'

#     return redirect(url_for('dashboard'))   

@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        mobile = request.form['mobile']
        sex = request.form['sex']
        number = request.form['text']
        address = request.form['address']

        
        try:
            cursor.execute("INSERT INTO appointment (fname, lname, email, mobile, sex, number, address) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (fname, lname, email, mobile, sex, number, address))
           
            conn.commit()
            return redirect(url_for('dashboard'))
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            return redirect(url_for('dashboard'))    
    else:
        pass

@app.route("/dashboard")
def dashboard():
    try:
        cursor.execute("SELECT * FROM appointment")
        value = cursor.fetchall()
        # cursor.close()  # Close the cursor after fetching data
        return render_template('dashboard.html', data=value)
    except mysql.connector.Error as e:
        print("Error executing SQL query:", e)
        return "Error fetching data from the database"
@app.route("/update/<patient_ID>")
def update(patient_ID):
    cursor.execute("select * from appointment where patient_ID=%s",( patient_ID,))
    value=cursor.fetchone()
    return render_template('edit.html', data=value)
# @app.route('/update/<int:ID>', methods=['GET', 'POST'])
# def update(ID):
#     msg = ''
#     if 'loggedin' in session:
#         if request.method == 'POST' and 'comment' in request.form and 'discription' in request.form:
#             comment = request.form['comment']
#             discription = request.form['discription']
#             try:
#                 cursor.execute('UPDATE user_comments SET comment = %s, discription = %s WHERE comm_id = %s', (comment, discription, ID))
#                 conn.commit()
#                 msg = 'Story updated successfully!'
#             except mysql.connector.Error as e:
#                 print("Error executing SQL query:", e)
#                 msg = 'An error occurred. Please try again later.'
#             return redirect(url_for('dashboard'))
#         cursor.execute('SELECT * FROM user_comments WHERE comm_id = %s', (ID,))
#         story = cursor.fetchone()
#         if story:
#             return render_template('update_comment.html', story=story)
#         else:
#             msg = 'Story not found!'
#     return redirect(url_for('login'))

@app.route('/edit',methods=['POST','GET'])
def edit():
    if request.method == 'POST':
        patient_ID= request.form['patient_ID']
        # print("ID in edit:", ID)
        # id=request.form['ID']
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        mobile = request.form['mobile']
        sex = request.form['sex']
        appointment = request.form['text']
        description = request.form['address']

        
        try:
            # update_query='''update student_form set first_name=%s, last_name=%s, email'''
            cursor.execute("UPDATE appointment SET fname=%s, lname=%s, email=%s,mobile=%s,sex=%s,number=%s,address =%s WHERE  patient_ID=%s", (fname, lname, email,mobile,sex,appointment,description,   patient_ID))
            conn.commit()
            return redirect(url_for('dashboard'))
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            return redirect(url_for('dashboard'))    
    else:
        pass
@app.route("/delete/<patient_ID>")
def delete(patient_ID):
    try:
        cursor.execute("DELETE FROM appointment WHERE      patient_ID= %s", (patient_ID,))
        conn.commit()
        return redirect(url_for('dashboard'))
    except mysql.connector.Error as e:
        print("Error executing SQL query:", e)
        return redirect(url_for('dashboard'))
   
if __name__ == '__main__':
    app.run(debug=True)
