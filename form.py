from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.fields import FloatField
from wtforms.validators import DataRequired,length,EqualTo,ValidationError

from flask import Flask,render_template,flash,redirect,url_for
from flaskext.mysql import MySQL
from flask_bcrypt import Bcrypt

import pymysql

app=Flask(__name__)
app.secret_key="a2fe316b5479facc91981d2033b9b3f6"

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'shop'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql=MySQL(app)
bcrypt=Bcrypt(app)

class loginForm(FlaskForm):
    Username= StringField("Username",validators=[DataRequired(),length(min=2)])
    Password=PasswordField("Password",validators=[DataRequired(),length(min=2)])
    Remember=BooleanField("Remember Me")
    Submit=SubmitField("Login")

class regForm(FlaskForm):
    Username= StringField("Username",validators=[DataRequired(),length(min=2)])
    Password=PasswordField("Password",validators=[DataRequired(),length(min=2)])
    confirmPassword=PasswordField("Confirm Password",validators=[DataRequired(),length(min=2),EqualTo("Password")])
    admin=BooleanField("signup as admin?")
    Submit=SubmitField("Register")

    def validate_Username(self,Username):

        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("Select username from shopper where username=%s",[Username.data])
        user=cursor.fetchone()

        cursor.close()
        conn.close()

        if user and len(user)>0:
            raise ValueError("Username Already Exist")

class addItemForm(FlaskForm):
    Item_Name=StringField("Item Name",validators=[DataRequired(),length(min=2)])
    Price=FloatField("Price",validators=[DataRequired()])
    Picture=FileField("Image of Item",validators=[FileAllowed(["png","jpg"]),DataRequired()])
    Submit=SubmitField("Add Product")
