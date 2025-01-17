from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    names = ['John', 'Mary', 'Sally', 'Wes']
    return render_template("about.html", names=names)