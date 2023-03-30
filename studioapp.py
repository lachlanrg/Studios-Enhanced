from flask import Flask, render_template, jsonify
from database import load_products_from_db


app = Flask(__name__, template_folder='Templates')

# this is where I can add more html pages
# for each app route is another web page that is viewed
    

@app.route('/')
def login():
    return render_template('login_page.html')

@app.route('/home')
def home():
    products = load_products_from_db()
    return render_template('home.html', products=products)

@app.route('/student/')
def student():
    return render_template('student.html')

@app.route('/profile/')
def profile():
    return render_template('profile.html')

# This app route can convert the list of products into a json file. executed when placing route at end of url

#@app.route('/api/productjson/')
#def list_products():
#    return jsonify(PRODUCTS)


if __name__ == '__main__':
    app.run(debug=True)