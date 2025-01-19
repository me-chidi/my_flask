import os
from flask import Flask, render_template, request
from flask_mail import Mail, Message

app = Flask(__name__)
subscribers = []

app.config['DEBUG'] = 1
#setting up SMTP credentials
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('YLJNKMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('YLJNKPWD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    names = ['John', 'Mary', 'Sally', 'Wes']
    return render_template('about.html', names=names)

@app.route('/subscribe')
def subscribe():
    title = 'Subscribe to my email newsletter'
    return render_template('subscribe.html', title=title)

@app.route('/form', methods=['POST'])
def form():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email_addr')

    if not first_name or not last_name or not email:
        err_stmt = 'All Form Fields Required...'
        return render_template('subscribe.html', err_stmt=err_stmt,
                               first_name=first_name,
                                last_name=last_name,
                                email=email)

    #creating the msg obj
    msg = Message(subject=f'Welcome {first_name} {last_name}!',
                  sender=os.environ.get('YLJNKMAIL'),
                  recipients=[email])
    msg.body = 'You have been subscribed to my email newsletter!' 
    mail.send(msg) 

    subscribers.append(f'{first_name} {last_name} | {email}')
    title = 'Thank you!'
    return render_template('form.html', title=title, subscribers=subscribers)