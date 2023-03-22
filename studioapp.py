from flask import Flask, render_template
app = Flask(__name__, template_folder='Templates')

# this is where I can add more html pages
# for each app route is another web page that is viewed

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/student/')
def student():
    return render_template('student.html')

@app.route('/profile/')
def profile():
    return render_template('profile.html')


if __name__ == '__main__':
    app.run(debug=True)