import os
from flask import Flask, render_template, request, redirect
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.app_context().push() #solves the working out of context error
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friends.db'
#initialize the database
db = SQLAlchemy(app)

#Create db model
class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc)) 
    
    #Create a function to return a string when we add something
    def __repr__(self):
        return '<Name %r>' % self.id

subscribers = []

app.config['DEBUG'] = 1 #should set the app in debug mode
#setting up SMTP credentials
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('YLJNKMAI')
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

@app.route('/friends', methods=['GET', 'POST'])
def friends():
    title = 'About my friends'

    if request.method == 'POST':
        friend_name = request.form['name']
        new_friend = Friends(name=friend_name)

        #push to db
        try:
            db.session.add(new_friend)
            db.session.commit()
            return redirect('/friends')
        except:
            return "There was an error adding your friend"
        
    else:
        #return the list of friends
        friends = Friends.query.order_by(Friends.date_created)
        return render_template('friends.html', title=title, friends=friends)

#method that updates a selected friend
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    friend_to_update = Friends.query.get_or_404(id)

    if request.method == 'POST':
        friend_to_update.name = request.form['name']
        try:
            db.session.commit()
            return redirect('/friends')
        except:
            return 'There was a problem updating that friend'
    else:
        return render_template('update.html', friend_to_update=friend_to_update)

@app.route('/delete/<int:id>')
def delete(id):
    friend_to_delete = Friends.query.get_or_404(id)

    try:
        db.session.delete(friend_to_delete)
        db.session.commit()
        return redirect('/friends')

    except:
        return 'There was a problem deleting that friend'



@app.route('/subscribe')
def subscribe():
    title = 'Subscribe to my email newsletter'
    return render_template('subscribe.html', title=title)

#this method also sends mail to the subscriber
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
    mail.send(msg) #mail does not send bcs 2FA is req in the gmail acc

    subscribers.append(f'{first_name} {last_name} | {email}')
    title = 'Thank you!'
    return render_template('form.html', title=title, subscribers=subscribers)