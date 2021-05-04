from flask import render_template,Blueprint
from server import mysql,loginManager
import pymysql
from flask_login import current_user

@loginManager.user_loader
def load_user(user_id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("Select username,id,pword,is_admin from shopper where id=%s",[int(user_id)])
    result=cursor.fetchone()
    cursor.close() 
    conn.close()
    return user(result["username"],result["id"],result["is_admin"])

mainPrint=Blueprint("mainPrint",__name__)

@mainPrint.route("/")
@mainPrint.route("/home")
def lnding():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("Select * from product")
    result=cursor.fetchall()
    cursor.close() 
    conn.close()
    return render_template("home.html",products=result)
