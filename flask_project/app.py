#!/usr/local/bin/python3

from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, Form
from wtforms.validators import DataRequired, Length, EqualTo, Email
from fda import fda_api
from models import db, login, UserModel
from flask_login import current_user, login_user, login_required, logout_user

#DBUSER = 'stockmaj'
#DBPASS = 'password'
#DBHOST = 'db'
#DBPORT = '5432'
#DBNAME = 'pglogindb'

class loginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Username()])
    password = PasswordField(label='Password',validators=[DataRequired(), Length(min=6,max=16)])
    submit = SubmitField(label='Login')

class RegistrationForm(Form):
    username = StringField(label='Username', validators=[Length(min=6, max=25)])
    email = StringField(label='Email Address', validators=[Length(min=6, max=35)])
    password = PasswordField(label='New Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match'), Length(min=6,max=16)])
    confirm = PasswordField('Repeat Password')

app=Flask(__name__)
app.secret_key='a secret'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
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
        user = UserModel(email='stockmaj@uw.edu')
        user.set_password('password')
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
def fdaSite():
    return render_template('fda.html', mydata=fda_api())

@app.route('/about')
def about():
    return render_template('about.html', body="About")

@app.route('/login',methods=["POST", "GET"])
def login():
    msg = ""
    if current_user.is_authenticated:
        return redirect('/fda')
    form=loginForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            username=request.form["username"]
            pw=request.form["password"]
            user = UserModel.query.filter_by(username = username).first()
            if user is not None and user.check_password(pw):
                login_user(user)
                return redirect('/fda')
            else:
                msg = "Incorrect username and/or password."
                return render_template('login.html',msg = msg)
        else:
            return render_template('login.html', form=form)
    else:
            return render_template('login.html', form=form)

@app.route('/registration',methods=["POST", "GET"])
def registration():
    
    form = RegistrationForm(request.form)
    
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        
        # check to see if username exists
        user_username = UserModel.query.filter_by(username=username).first()
        if user_username:
			return "Username not available."
			
		user_email = UserModel.query.filter_by(email=email).first()
        if user_email:
			return "Email address already registered."
        
        #add user to db
        user = UserModel(email=email, username=username, password=password)
        db.session.add(user)
        return "Added User to Database."
        
        
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/home')

if __name__== "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
