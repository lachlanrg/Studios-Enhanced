from flask import Flask, render_template, jsonify
app = Flask(__name__, template_folder='Templates')


PRODUCTS = [
    { 
        'productname': 'Studio Management',
        'id': 1,
        'productowner': 'Wayne Brooks',
        'prerequisite': 'Studio A',
     },
     { 
        'productname': 'Rockets',
        'id': 2,
        'productowner': 'Valarie ',
        'prerequisite': 'Applications A',
    }
]

# this is where I can add more html pages
# for each app route is another web page that is viewed

@app.route('/')
def login():
    return render_template('login_page.html')

@app.route('/home')
def home():
    return render_template('home.html', products=PRODUCTS)

@app.route('/student/')
def student():
    return render_template('student.html')

@app.route('/profile/')
def profile():
    return render_template('profile.html')

# This app route can convert the list of products into a json file. executed when placing route at end of urla
@app.route('/api/productjson/')
def list_products():
    return jsonify(PRODUCTS)


if __name__ == '__main__':
    app.run(debug=True)