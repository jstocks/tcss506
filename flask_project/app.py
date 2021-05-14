#!/usr/local/bin/python3

from flask import Flask, render_template, request, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from fda import fda_api
from flask_login import current_user, login_user, login_required, logout_user
from models import db, login, UserModel

# cloud database info
# DBUSER = 'stockmaj'
# DBPASS = 'password'
# DBHOST = 'db'
# DBPORT = '5432'
# DBNAME = 'pglogindb'

# local database info
DBUSER = 'postgres'
DBPASS = 'password'
DBHOST = 'localhost'
DBPORT = '5432'
DBNAME = 'postgres'


class loginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Login')


class registrationForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=6, max=25)])
    email = StringField(label='Email',validators=[DataRequired(), Email()])
    password = PasswordField(label='New Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match'), Length(min=6,max=16)])
    confirm = PasswordField(label='Repeat Password', validators=[DataRequired(), Length(min=6,max=16)])
    submit = SubmitField(label='Register')


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

db.init_app(app)
login.init_app(app)
login.login_view = 'login'


@app.before_first_request  # decorator to make the actual database
def create_table():
    db.create_all()
    try:
        user = UserModel()
        user.set_password('')
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        return


@app.route('/')
def baseSite():
    return redirect("/login")


@app.route('/home')
def homepage():
    return render_template('home.html')


@app.route('/fda')
@login_required
def fda_site():
    return render_template('fda.html', mydata=fda_api())


@app.route('/about')
def about():
    return render_template('about.html', body="About")


@app.route('/login',methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect('/fda')
    form = loginForm()
    if form.validate_on_submit():
        if request.method == "POST":
            username = request.form["username"]
            pw = request.form["password"]
            user = UserModel.query.filter_by(username=username).first()
            if user is not None and user.check_password(pw):
                login_user(user)
                flash('You are successfully logged in.', "info")
                return redirect('/fda')
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

        addUser(username, email, password)
        flash('Thanks for registering', "info")

        return redirect('/login')

    return render_template('registration.html', form=form)


def addUser(username, email, password):
    user = UserModel(username=username)
    user.set_password(password)
    user.email = email
    db.session.add(user)
    db.session.commit()


@app.route('/logout')
def logout():
    logout_user()
    flash('You are successfully logged out.', "info")
    return redirect('/home')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
