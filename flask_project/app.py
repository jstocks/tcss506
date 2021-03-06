#!/usr/local/bin/python3
import os
from flask import Flask, render_template, request, redirect, flash
from flask_googlemaps import GoogleMaps
from flask_mail import Mail
from flask_wtf import FlaskForm
from flaskthreads import AppContextThread
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from api import find_recall, graph_recall, map_recall
from device import device_api
from drug import drug_api
from food import food_api
from flask_login import current_user, login_user, login_required, logout_user
from models import db, login, UserModel
from db_access import Database_access
from producer_consumer import producer_thread, consumer_thread


# cloud database info
# DBUSER = 'xxxxxx'
# DBPASS = 'xxxxxx'
# DBHOST = 'xxxxxx'
# DBPORT = 'xxxxxx'
# DBNAME = 'xxxxxx'

# local database info
DBUSER = 'postgres'
DBPASS = 'password'
DBHOST = '172.17.0.2'
DBPORT = '5432'
DBNAME = 'postgres'

EMAIL_ADDRESS = os.environ.get('EMAIL_ID_FDA')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS_FDA')


class loginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Login')


class registrationForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=6, max=25)])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='New Password',
                             validators=[DataRequired(), EqualTo('confirm', message='Passwords must match'),
                                         Length(min=6, max=16)])
    confirm = PasswordField(label='Repeat Password', validators=[DataRequired(), Length(min=6, max=16)])
    submit = SubmitField(label='Register')


class subscriptionForm(FlaskForm):
    subscribe = RadioField(label='Subscribe for weekly updates to the FDA device recall database',
                           choices=[(True, 'subscribe for weekly updates'), (False, 'unsubscribe')])
    submit = SubmitField(label='Done')


class deleteaccForm(FlaskForm):
    delete_account = RadioField(label='Delete your account', choices=[(True, 'yes'), (False, 'no')])
    submit = SubmitField(label='Done')


class passwordresetForm(FlaskForm):
    password1 = PasswordField(label='Reset Password', validators=[DataRequired(), Length(min=6, max=16)])
    password2 = PasswordField(label='Retype new Password', validators=[DataRequired(), Length(min=6, max=16)])
    submit = SubmitField(label='Done')


app = Flask(__name__)
app.secret_key = 'a secret'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}'.format(
        user=DBUSER,
        passwd=DBPASS,
        host=DBHOST,
        port=DBPORT,
        db=DBNAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
mail = Mail(app)  # instantiate the mail class

# configuration of mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = EMAIL_ADDRESS
app.config['MAIL_PASSWORD'] = EMAIL_PASSWORD
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

db.init_app(app)
login.init_app(app)
login.login_view = 'login'
GoogleMaps(app, key="AIzaSyBgvpdbo-uHRFsr3QPIqoq_P0jAnxIB9UQ")
db_acc = Database_access(db)


@app.before_first_request  # decorator to make the actual database
def create_table():
    """
    Creates the database. Inserts two users into the users table.
    Creates and starts the producer and consumer thread
    to send weekly email updates to the subscribers
    :return: None
    """
    # db creation
    db.create_all()
    try:
        user = UserModel(email='sribadevelopment@gmail.com', username='rsriba', subscription=True)
        user.set_password('password')
        db.session.add(user)
        user1 = UserModel(email='fdarecalltest@gmail.com', username='sribar', subscription=True)
        user1.set_password('password')
        db.session.add(user1)
        db.session.commit()
    except Exception as e:
        return
    # Producer thread - to send message to SQS
    # Consumer thread - to receive message from SQS
    t1 = AppContextThread(target=producer_thread, daemon=True, args=(db_acc,))
    t2 = AppContextThread(target=consumer_thread, daemon=True, args=(db_acc, app, mail, EMAIL_ADDRESS, ))
    t1.start()
    t2.start()


@app.route('/')
def baseSite():
    return redirect("/login")


@app.route('/home')
def homepage():
    return render_template('home.html')


@app.route('/fda')
@login_required
def fda_site():
    return render_template('fda.html', mydata=device_api())


@app.route('/fdagraph')
@login_required
def fdagraph():
    return render_template('fda_plotly.html', graphJSON=graph_recall())


@app.route('/fdamap')
@login_required
def fdamap():
    return render_template('fda_map.html', mymap=map_recall())


@app.route('/about')
@login_required
def about():
    return render_template('about.html', body="About")


@app.route('/devices')
@login_required
def devices():
    return render_template('devices.html', mydata=device_api(
        request.args.get("limit"),
        request.args.get("company"),
        request.args.get("from_date"),
        request.args.get("to_date")
    ))


@app.route('/drug')
@login_required
def drug():
    return render_template('drug.html', mydata=drug_api(
        request.args.get("limit"),
        request.args.get("company"),
        request.args.get("from_date"),
        request.args.get("to_date")
    ))


@app.route('/food')
@login_required
def food():
    return render_template('food.html', mydata=food_api(
        request.args.get("limit"),
        request.args.get("company"),
        request.args.get("from_date"),
        request.args.get("to_date")
    ))


@app.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect('/devices')
    form = loginForm()
    if form.validate_on_submit():
        if request.method == "POST":
            username = request.form["username"]
            pw = request.form["password"]
            user = UserModel.query.filter_by(username=username).first()
            if user is not None and user.check_password(pw):
                login_user(user)
                flash('You are successfully logged in.', "info")
                return redirect('/home')
            else:
                flash('Incorrect username and/or password.', "info")
                return render_template('login.html', form=form)
        return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = registrationForm()

    if request.method == 'POST' and form.validate():
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        # check to see if username exists
        user_username = UserModel.query.filter_by(username=username).first()
        if user_username:
            flash("Username not available.", "info")
            return render_template('registration.html', form=form)

        user_email = UserModel.query.filter_by(email=email).first()
        if user_email:
            flash("Email address already registered.", "info")
            return render_template('registration.html', form=form)

        # user = UserModel([form.email.data, form.username.data, form.password.data])

        db_acc.addUser(username, email, password)
        flash('Thanks for registering', "info")

        return redirect('/login')

    return render_template('registration.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are successfully logged out.', "info")
    return redirect('/home')


@app.route('/settings', methods=["POST", "GET"])
@login_required
def settings():
    form = subscriptionForm()
    if form.validate_on_submit():
        if request.method == "POST":
            subscribe = request.form["subscribe"]
            if subscribe == "True":
                subscribe = True
            else:
                subscribe = False
            db_acc.updateSubscription(current_user.username, subscribe)
            result = db_acc.test_subscription_update(current_user.username)
            flash(f"Subscription Status changed to:{result}")
        return redirect('/home')
    else:
        return render_template('settings.html', form=form)


@app.route('/resetpassword', methods=["POST", "GET"])
@login_required
def resetpassword():
    form = passwordresetForm()
    if form.validate_on_submit():
        if request.method == "POST":
            pw1 = request.form["password1"]
            pw2 = request.form["password2"]
            if pw1 == pw2:
                db_acc.reset_password(current_user.username, pw1)
                flash("Password reset successfully!!!")
            else:
                flash("Passwords don't match. Retype!!!")
                return render_template('settings_passwordreset.html', form=form)
        return redirect('/home')
    else:
        return render_template('settings_passwordreset.html', form=form)


@app.route('/deleteaccount', methods=["POST", "GET"])
@login_required
def deleteaccount():
    form = deleteaccForm()
    if form.validate_on_submit():
        if request.method == "POST":
            delete_acc = request.form["delete_account"]
            if delete_acc == 'True':
                db_acc.delete_record(current_user.username)
        return redirect('/home')
    else:
        return render_template('settings_delete.html', form=form)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
