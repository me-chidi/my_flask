from flask import Flask, render_template, request

app = Flask(__name__)
subscribers = []

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


    subscribers.append(f'{first_name} {last_name} | {email}')
    title = 'Thank you!'
    return render_template('form.html', title=title, subscribers=subscribers)