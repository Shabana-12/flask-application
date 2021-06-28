from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask_mail import Mail, Message
mail = Mail()
app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '******'
app.config['MYSQL_DB'] = 'pythonlogin'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'apexinfotechexcellenceco@gmail.com'
app.config['MAIL_PASSWORD'] = '********'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

# Intialize MySQL
mysql = MySQL(app)
# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests

# email=''
mail = Mail(app)
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form:
        # Create variables for easy access
        name = request.form['name']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM user WHERE name = %s AND password = %s', (name, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['name'] = account['name']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect name/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    # Redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests


@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''

    if request.method == 'POST' and 'name' in request.form and 'dob' in request.form and 'gender' in request.form and 'password' in request.form and 'phone' in request.form and 'email' in request.form and 'address' in request.form:
        name = request.form['name']
        dob = request.form['dob']
        gender = request.form['gender']
        password = request.form['password']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        # Create variables for easy access

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE name = %s', (name,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Username must contain only characters and numbers!'
        elif not name or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute("INSERT INTO user(name, password, email, phone, gender, dob, address) VALUES(%s, %s, %s, %s, %s, %s, %s)",
                           (name, password, email, phone, gender, dob, address))

        mysql.connection.commit()
        msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)
# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users


@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', name=session['name'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users


@app.route('/pythonlogin/profile')
@app.route('/profile')
def profile():
 # Check if account exists using MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor.execute('SELECT * FROM user WHERE name = %s',
                       [session['name']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/back')
def back():
    return render_template('home.html')


@app.route("/reset", methods=['GET', 'POST'])
def reset():
    if request.method == 'GET':
        return render_template("RESET.html")
    global email
    email = request.form['email']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
    account = cursor.fetchone()
    # If account exists show error and validation checks
    
    if account:
        msg = Message(
            'Confirm Email', sender='apexinfotechexcellenceco@gmail.com', recipients=[email])
        msg.body = ('Your link is '+'http://127.0.0.1:5000/reset_email')
        mail.send(msg)
        flash ("Please Check your mail link sent for password reset")
        return redirect(url_for('reset'))

    else:
        flash("Email-Id is not Registered Please Enter correct email address!!!!")
        return redirect(url_for('reset'))


@app.route("/reset_email", methods=['GET', 'POST'])

def reset_email():
    
    if request.method == 'GET':
        return render_template("reset_email.html")
    new_pwd = request.form['pwd']
    con_pwd = request.form['cpwd']
    if(new_pwd == con_pwd):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE user SET PASSword=%s WHERE email=%s",
                    (new_pwd, email))
        mysql.connection.commit()
        flash('your password reset successfully')
        
        return redirect(url_for('login'))
    else:
        flash("Passwords did not match try again!!!!")
        return redirect(url_for('reset_email'))


if __name__ == "__main__":
    app.run()
