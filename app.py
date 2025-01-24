import os
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

# General notes before you go further:
# all times are in utc

app = Flask(__name__)
app.app_context().push() #solves the working out of context error
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.environ.get('FSKY') #use env var. This stores the session cookies
#setting up SMTP credentials
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('YLJNKMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('YLJNKPWD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

#initialize the database
db = SQLAlchemy(app)
#initialize migrate
migrate = Migrate(app, db)
#initialize the mail client
mail = Mail(app)
#initialize Bcrypt
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

#reloads the user obj from the user id stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

subscribers = []

#Create db models
class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc)) 
    
    #Create a function to return a string when we add something
    def __repr__(self):
        return '<Name %r>' % self.id

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={'placeholder': 'Username'})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)],
                             render_kw={'placeholder': 'Password'})
    submit = SubmitField('Register')

    #prevents repeat usernames in db
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("Username taken! Try again.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
                           render_kw={'placeholder': 'Username'})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)],
                             render_kw={'placeholder': 'Password'})
    submit = SubmitField('Login')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
        #authentication logic for a user before login
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
    return render_template('index.html', form=form)

#logs out user then redirects back to home page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    #creating a new user
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_pwd = bcrypt.generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_pwd)
            try:
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('index'))
            except:
                return 'There was an error creating user'
    else:
        return render_template('register.html', form=form)

@app.route('/about')
@login_required
def about():
    names = ['John', 'Mary', 'Sally', 'Wes']
    return render_template('about.html', names=names)

@app.route('/friends', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def delete(id):
    friend_to_delete = Friends.query.get_or_404(id)

    try:
        db.session.delete(friend_to_delete)
        db.session.commit()
        return redirect('/friends')

    except:
        return 'There was a problem deleting that friend'

@app.route('/subscribe')
@login_required
def subscribe():
    title = 'Subscribe to my email newsletter'
    return render_template('subscribe.html', title=title)

#this method sends mail to the subscriber
@app.route('/form', methods=['POST'])
@login_required
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