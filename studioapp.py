from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from database import load_products_from_db
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb
import re
import os
import ssl


app = Flask(__name__, template_folder='Templates')
app.secret_key = os.urandom(24)
app.secret_key = 'uwbdu8jJ89WJH4bjos834Hbu8Jhfiueak99bn0bbjsdf'


ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

app.config['MYSQL_SSL_CTX'] = ssl_context

ssl = {'ca': '/etc/ssl/cert.pem'}
conn = MySQLdb.connect ( 
    host='aws.connect.psdb.cloud', 
    user='p3tdqa99eyp5ihs04p9m', 
    password='pscale_pw_ReSZao9FFuxG5X7dYrZu7dfL0vryGybgYNI2k7Oc7Dg', 
    db='studiosenhanced', ssl=ssl
)

app.config['MYSQL_SSL_CA'] = '/etc/ssl/cert.pem'
app.config['MYSQL_SSL_CERT'] = 'client-cert.pem'
app.config['MYSQL_SSL_KEY'] = 'client-key.pem'

# Initialize MySQL
app.config['MYSQL_HOST'] = 'aws.connect.psdb.cloud'
app.config['MYSQL_USER'] = 'p3tdqa99eyp5ihs04p9m'
app.config['MYSQL_PASSWORD'] = 'pscale_pw_ReSZao9FFuxG5X7dYrZu7dfL0vryGybgYNI2k7Oc7Dg'
app.config['MYSQL_DB'] = 'studiosenhanced'


mysql = MySQL(app)

# this is where I can add more html pages
# for each app route is another web page that is viewed
    

@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()
        cursor.close()
        # If account exists in accounts table in mysql database
        if account:
            # Create session data
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']

            mysql.connection.commit()
            mysql.connection.close()

            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # If account doesnt exist or email/password incorrect use this message
            msg = 'Incorrect email/password!'
    return render_template('login_page.html', msg=msg)


@app.route('/logout')
def logout():
    # Remove session data and log out the user
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('email', None)
   # Redirect to login page
   return redirect(url_for('login'))
    

@app.route('/home/')
def home():
    if 'loggedin' in session:
        products = load_products_from_db()
        # User is loggedin show them the home page
        return render_template('home.html', id=session['id'], products=products)
    return redirect(url_for('login'))

@app.route('/student/')
def student():
    return render_template('student.html')

@app.route('/profile/')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
    

# This app route can convert the list of products into a json file. executed when placing route at end of url

@app.route('/api/productjson/')
def list_products():
    products = load_products_from_db()
    return jsonify(products)


if __name__ == '__main__':
    app.run(debug=True)