from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.fields import FloatField
from wtforms.validators import DataRequired,length,EqualTo,ValidationError

from server import mysql

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