from flask import render_template,Blueprint
from server import mysql,loginManager
import pymysql
from flask_login import current_user

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
