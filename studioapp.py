from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash, get_flashed_messages, make_response
from database import load_products_from_db, load_product_from_db
import MySQLdb.cursors
import mysql.connector
from mysql.connector.constants import ClientFlag
from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import cursor
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange
import re
import os
import csv
import io
from io import StringIO
from datetime import datetime
import ssl
from models import db, Account

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, template_folder='Templates')
app.secret_key = os.urandom(24)

# Initialize MySQL

# connection = MySQLdb.connect(
#   host= os.getenv("HOST"),
#   user=os.getenv("USERNAME"),
#   passwd= os.getenv("PASSWORD"),
#   db= os.getenv("DATABASE"),
#   ssl_mode = "VERIFY_IDENTITY",
#   ssl      = {
   ### "ca": "/Users/lachlangreig/Documents/Studios-Enhanced/cert.pem"
 #    "ca": "/etc/secrets/cert.pem"
 #  }
# )

config = {
    'user': os.getenv("USERNAME"),
    'password': os.getenv("PASSWORD"),
    'host': os.getenv("HOST"),
    'database': os.getenv("DATABASE"),
    #'ssl_ca': '/etc/secrets/cert.pem', 
    'ssl_ca': '/Users/lachlangreig/Documents/Studios-Enhanced/cert.pem', 
    #'use_pure': True,
    #'client_flags': [ClientFlag.SSL],
}

connection = mysql.connector.connect(**config)

@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        
        cursor = connection.cursor(dictionary=True) 
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()
        cursor.close()
        
        # If account exists in accounts table in the MySQL database
        if account:
            # Create session data
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            session['role'] = account['role']

            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # If account doesn't exist or email/password incorrect use this message
            msg = 'Incorrect email/password!'
    return render_template('login_page.html', msg=msg)


@app.route('/logout')
def logout():
    # Remove session data and log out the user
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('email', None)
   session.pop('role', None)
   return redirect(url_for('login'))
    

@app.route('/home/')
def home():
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.close()  
        products = load_products_from_db()
        # User is loggedin show them the home page
        return render_template('homev2.html', id=session['id'], products=products, account=account)
    return redirect(url_for('login'))


@app.route('/product/<int:id>')
def show_product(id):
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.close() 
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM products WHERE id = %s"
        cursor.execute(query, (id,))
        product = cursor.fetchone()
        cursor.close()
        return render_template('product.html', product=product, account=account)
    return redirect(url_for('login'))


@app.route('/enrol/<int:product_id>', methods=['POST'])
def enrol(product_id):
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        user_id = session['id']

        product_query = "SELECT title FROM products WHERE id = %s"
        cursor.execute(product_query, (product_id,))
        product = cursor.fetchone()
        if product is None:
            cursor.close()
            db.close()
            return "Product not found", 404  

        product_title = product['title']

        # Update the current product with the product's title
        update_query = "UPDATE accounts SET current_product = %s WHERE id = %s"

        cursor.execute(update_query, (product_title, user_id))
        connection.commit()
        cursor.close()

        flash('Successfully enrolled in ' + product_title)

        return redirect(url_for('show_product', id=product_id))
    return redirect(url_for('login'))

 
@app.route('/pref1/<int:product_id>', methods=['POST'])
def pref1(product_id):
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        user_id = session['id']

        product_query = "SELECT title FROM products WHERE id = %s"
        cursor.execute(product_query, (product_id,))
        product = cursor.fetchone()
        if product is None:
            cursor.close()
            db.close()
            return "Product not found", 404  
        
        product_title = product['title']
        # Update the prefernce 1 with the product's title
        update_query = "UPDATE accounts SET product_preference1 = %s WHERE id = %s"
        cursor.execute(update_query, (product_title, user_id))
        connection.commit()
        cursor.close()

        #Updating the product_accounts table

        # student_id = session['id']
       #  preference = 1
       #  enrolled_at = None
       #  cursor = connection.cursor()
        # Get the product title using the product_id
       #  query = "SELECT title FROM products WHERE id = %s"
       #  cursor.execute(query, (product_id,))

       #  product_title = product['title']
       #  cursor.fetchall()
        # Insert a new row into the product_accounts table
       #  query = "INSERT INTO product_accounts (product_title, student_id, preference, enrolled_at) VALUES (%s, %s, %s, %s)"
       #  cursor.execute(query, (product_title, student_id, preference, enrolled_at))
       #  connection.commit()
       #  cursor.close()

        flash(product_title + ' is now your first preference!' )

        return redirect(url_for('show_product', id=product_id))
    return redirect(url_for('login'))


@app.route('/pref2/<int:product_id>', methods=['POST'])
def pref2(product_id):
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        user_id = session['id']

        product_query = "SELECT title FROM products WHERE id = %s"
        cursor.execute(product_query, (product_id,))
        product = cursor.fetchone()
        if product is None:
            cursor.close()
            db.close()
            return "Product not found", 404  

        product_title = product['title']

        # Update the prefernce 2 with the product's title
        update_query = "UPDATE accounts SET product_preference2 = %s WHERE id = %s"
        cursor.execute(update_query, (product_title, user_id))
        connection.commit()
        cursor.close()

        flash(product_title + ' is now your second preference!' )

        return redirect(url_for('show_product', id=product_id))
    return redirect(url_for('login'))


@app.route('/pref3/<int:product_id>', methods=['POST'])
def pref3(product_id):
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        user_id = session['id']

        product_query = "SELECT title FROM products WHERE id = %s"
        cursor.execute(product_query, (product_id,))
        product = cursor.fetchone()
        if product is None:
            cursor.close()
            db.close()
            return "Product not found", 404  

        product_title = product['title']

        # Update the prefernce 3 with the product's title
        update_query = "UPDATE accounts SET product_preference3 = %s WHERE id = %s"
        cursor.execute(update_query, (product_title, user_id))
        connection.commit()
        cursor.close()

        flash(product_title + ' is now your third preference!' )

        return redirect(url_for('show_product', id=product_id))
    return redirect(url_for('login'))
    

class ProductForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    owner = StringField('Owner', validators=[DataRequired()])
    prerequisites = TextAreaField('Prerequisites')
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create Product')


@app.route('/create_product/', methods=['GET', 'POST'])
def create_product():
    form = ProductForm()
    account = None
    title = None
    if form.validate_on_submit():
        title = form.title.data
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.close() 

        if form.validate_on_submit():
            title = form.title.data
            product_owner = form.owner.data
            prerequisites = form.prerequisites.data
            description = form.description.data

            cursor = connection.cursor(dictionary=True)
            cursor.execute("INSERT INTO products(title, product_owner, prerequisites, description) VALUES(%s, %s, %s, %s)", 
                        (title, product_owner, prerequisites, description))
            connection.commit()
            cursor.close()
            flash('Successfully submitted the product with title: ' + title )

    return render_template('create_product.html', form=form, account=account)


@app.route('/product/<int:id>/delete', methods=['POST'])
def delete_product(id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    cursor.close()
    if 'loggedin' in session and session['role'] == 'admin':

        cursor = connection.cursor()
        query = "DELETE FROM products WHERE id = %s"
        cursor.execute(query, (id,))
        connection.commit()
        cursor.close()
        flash("Product successfully deleted.", "success")
        return redirect(url_for('home'))
    else:
        return render_template('unauthorised.html', message='Access Denied: You must be an Admin to access this page', account=account)


@app.route('/profile/')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.close()  # Close the cursor
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

class FeedbackForm(FlaskForm):
    group = StringField('Group', validators=[DataRequired()])
    session_number = SelectField('Session Number', choices=[('1', '1'), ('2', '2'), ('3', '3')], validators=[DataRequired()])
    positives = TextAreaField('What did the group do well?', validators=[DataRequired()])
    improvements = TextAreaField('What can they improve upon?', validators=[DataRequired()])
    impression = IntegerField('Overall impression of the pitch (rate 1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    tips = TextAreaField('Any tips/points of interest')
    submit = SubmitField('Submit')

@app.route('/feedback/', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    account = None
    group = None
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.close()

        if form.validate_on_submit():
            group = form.group.data
            session_number = form.session_number.data
            positives = form.positives.data
            improvements = form.improvements.data
            impression = form.impression.data
            tips = form.tips.data

            cursor = connection.cursor(dictionary=True)
            cursor.execute("INSERT INTO feedback(groupName, session_number, positives, improvements, impression, tips) VALUES (%s, %s, %s, %s, %s, %s)", (group, session_number, positives, improvements, impression, tips))
            connection.commit()
            cursor.close()
            flash('Successfully submitted the feedback for group: ' + group )

    return render_template('feedback.html', form=form, account=account)

@app.route('/preferences/')
def preferences():
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.close()
        # Fetch all product titles

        cursor = connection.cursor(dictionary=True)
        accounts_query = '''
        SELECT 
            id, 
            first_name,
            last_name,
            product_preference1,
            product_preference2,
            product_preference3,
            current_product
        FROM 
            accounts;
        '''
        cursor.execute(accounts_query)
        accounts = cursor.fetchall()
        cursor.close()

        # Create a dictionary of products and their associated accounts
        products = {}
        for account in accounts:
            # Check if the current account has enrolled in a product
            if account['current_product'] is not None:
                if account['current_product'] not in products:
                    products[account['current_product']] = {'enrolled_accounts': [], 'preference_accounts': []}
                products[account['current_product']]['enrolled_accounts'].append({'id': account['id'], 'first_name': account['first_name'], 'last_name': account['last_name']})
            # Check if the current account has a preference for a product
            for i in range(1, 4):
                preference_col = f'product_preference{i}'
                if account[preference_col] is not None:
                    if account[preference_col] not in products:
                        products[account[preference_col]] = {'enrolled_accounts': [], 'preference_accounts': []}
                    products[account[preference_col]]['preference_accounts'].append({'id': account['id'], 'first_name': account['first_name'], 'last_name': account['last_name']})

        # Render the template with the products and their associated accounts
        return render_template('preferences.html', products=products, account=account)

    return redirect(url_for('login'))

class Discussion(db.Model):
    __tablename__ = 'discussions'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/discussions/', methods=['GET', 'POST'])
def discussions():
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()

        if request.method == 'POST':
            subject = request.form.get('subject')
            content = request.form.get('content')
            timestamp = datetime.utcnow()

            cursor.execute(
                'INSERT INTO discussions (first_name, last_name, subject, content, timestamp) VALUES (%s, %s, %s, %s, %s)',
                (account['first_name'], account['last_name'], subject, content, timestamp))

            connection.commit()

            cursor.execute('SELECT * FROM discussions ORDER BY timestamp DESC')
            discussions = cursor.fetchall()
            
            cursor.close()
            return render_template('discussions.html', discussions=discussions, account=account)

        else:
            cursor.execute('SELECT * FROM discussions ORDER BY timestamp DESC')
            discussions = cursor.fetchall()
            cursor.close()
            return render_template('discussions.html', discussions=discussions, account=account)


    return redirect(url_for('login'))

@app.route('/discussions/delete/<int:id>', methods=['POST'])
def delete_discussion(id):
    if 'loggedin' in session and session['role'] == 'admin':
        cursor = connection.cursor(dictionary=True)
        cursor.execute('DELETE FROM discussions WHERE id = %s', (id,))
        connection.commit()
        cursor.close()
        flash('Discussion successfully deleted')
    return redirect(url_for('discussions'))

@app.route('/download_preference_csv/')
def download_preference_csv():
    if 'loggedin' in session:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        
        # Fetch all product titles
        accounts_query = '''
        SELECT 
            id, 
            first_name,
            last_name,
            email,
            product_preference1,
            product_preference2,
            product_preference3,
            current_product
        FROM 
            accounts;
        '''
        cursor.execute(accounts_query)
        accounts = cursor.fetchall()
        cursor.close()

        # Create a dictionary of products and their associated accounts
        products = {}
        for account in accounts:
            # Check if the current account has enrolled in a product
            if account['current_product'] is not None:
                if account['current_product'] not in products:
                    products[account['current_product']] = {'enrolled_accounts': [], 'preference_accounts': []}
                products[account['current_product']]['enrolled_accounts'].append(account)
            # Check if the current account has a preference for a product
            for i in range(1, 4):
                preference_col = f'product_preference{i}'
                if account[preference_col] is not None:
                    if account[preference_col] not in products:
                        products[account[preference_col]] = {'enrolled_accounts': [], 'preference_accounts': []}
                    products[account[preference_col]]['preference_accounts'].append(account)

        # Create CSV content
        csv_content = []
        header = ['Product', 'Enrolled Accounts', 'Preference Accounts']
        csv_content.append(header)
        for product_id, product_accounts in products.items():
            enrolled_accounts = ", ".join([f"{account['first_name']} {account['last_name']}" for account in product_accounts['enrolled_accounts']])
            preference_accounts = ", ".join([f"{account['first_name']} {account['last_name']}" for account in product_accounts['preference_accounts']])
            csv_content.append([product_id, enrolled_accounts, preference_accounts])

        # Convert CSV content to a string
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerows(csv_content)
        csv_string = si.getvalue()

        # Create a response with the CSV string as the body
        response = make_response(csv_string)
        response.headers["Content-Disposition"] = "attachment; filename=preferences_csv.csv"
        response.headers["Content-type"] = "text/csv"
        return response
    return redirect(url_for('login'))

@app.route('/admin/')
def admin():
    account = None
    # Check if user is loggedin
    if 'loggedin' in session and session['role'] == 'admin':
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.close()
        return render_template('admin.html', account=account)
    # User does not have admin role
    return render_template('unauthorised.html', message='Access Denied: You must be an Admin to access this page', account=account)

@app.route('/download_account_csv')
def download_account_csv():
    if 'loggedin' in session and session['role'] == 'admin':

        cursor = connection.cursor(dictionary=True)

        # Fetch all accounts' information
        account_query = "SELECT * FROM accounts"
        cursor.execute(account_query)
        accounts = cursor.fetchall()
        if accounts is None:
            cursor.close()
            return "No accounts found", 404

        cursor.close()

        # Create CSV content
        csv_content = []
        header = accounts[0].keys()  
        csv_content.append(header)
        for account in accounts:
            csv_content.append(list(account.values()))

        # Convert CSV content to a string
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerows(csv_content)
        csv_string = si.getvalue()

        # Create a response with the CSV string as the body
        response = make_response(csv_string)
        response.headers["Content-Disposition"] = "attachment; filename=accounts.csv"
        response.headers["Content-type"] = "text/csv"
        return response
    return redirect(url_for('login'))

@app.route('/download_product_accounts_csv')
def download_product_accounts_csv():
    # Execute the SQL query to get the account information
    if 'loggedin' in session and session['role'] == 'admin':
        cursor = connection.cursor(dictionary=True)

        # Fetch all accounts' information
        product_query = '''
        SELECT 
            id, 
            product_preference1,
            product_preference2,
            product_preference3,
            current_product
        FROM 
            accounts;
        '''
        cursor.execute(product_query)
        accounts = cursor.fetchall()
        if accounts is None:
            cursor.close()
            return "No accounts found", 404

        cursor.close()

        # Create CSV content
        csv_content = []
        header = accounts[0].keys()  
        csv_content.append(header)
        for account in accounts:
            csv_content.append(list(account.values()))

        # Convert CSV content to a string
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerows(csv_content)
        csv_string = si.getvalue()

        # Create a response with the CSV string as the body
        response = make_response(csv_string)
        response.headers["Content-Disposition"] = "attachment; filename=product_accounts.csv"
        response.headers["Content-type"] = "text/csv"
        return response
    return redirect(url_for('login'))


@app.route('/download_feedback_csv')
def download_feedback_csv():

    if 'loggedin' in session and session['role'] == 'admin':

        cursor = connection.cursor(dictionary=True)

        # Fetch all feedback information
        feedback_query = "SELECT * FROM feedback"
        cursor.execute(feedback_query)
        feedbacks = cursor.fetchall()
        if feedbacks is None:
            cursor.close()
            return "No feedbacks found", 404

        cursor.close()

        # Create CSV content
        csv_content = []
        header = feedbacks[0].keys()  
        csv_content.append(header)
        for feedback in feedbacks:
            csv_content.append(list(feedback.values()))

        # Convert CSV content to a string
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerows(csv_content)
        csv_string = si.getvalue()

        # Create a response with the CSV string as the body
        response = make_response(csv_string)
        response.headers["Content-Disposition"] = "attachment; filename=feedback.csv"
        response.headers["Content-type"] = "text/csv"
        return response
    return redirect(url_for('login'))


@app.route('/api/productjson/')
def list_products():
    products = load_products_from_db()
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True)