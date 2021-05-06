from flask import Blueprint,render_template,url_for,flash,redirect,request,session
from flask_login import login_required,login_user,logout_user,current_user
from server.users.form import loginForm, regForm
from server import mysql,bcrypt
from server.model import user
import pymysql

userPrint=Blueprint("userPrint",__name__)

@userPrint.route("/user/logout")
def logout():
    logout_user()
    return redirect(url_for("mainPrint.lnding"))

@userPrint.route("/user/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("mainPrint.lnding"))

    loginpage=loginForm()
    if loginpage.validate_on_submit():

        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        cursor.execute("Select username,id,pword,is_admin from shopper where username=%s",[loginpage.Username.data])
        result=cursor.fetchone()
        cursor.close() 
        conn.close()

        if result and len(result)>0 and bcrypt.check_password_hash(result["pword"],loginpage.Password.data):
            loggedin_user=user(result["username"],result["id"],result["is_admin"])
            login_user(loggedin_user,remember=loginpage.Remember.data)
            flash('Welcome {}'.format(loginpage.Username.data),"success")
            next_pg=request.args.get('next')
            
            return redirect(next_pg) if next_pg else redirect(url_for("mainPrint.lnding"))
        else:
            flash('login failed. Make sure you are signed up.',"warning")
        
    return render_template("Login.html",form=loginpage)

@userPrint.route("/user/signup",methods=["GET","POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("mainPrint.lnding"))

    loginpage=regForm()
    if loginpage.validate_on_submit():
        
        Hashed_pwd=bcrypt.generate_password_hash(loginpage.Password.data).decode('utf-8')
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("insert into shopper (username,pword,is_admin) value (%s,%s,%s)",[loginpage.Username.data,Hashed_pwd,loginpage.admin.data])
        conn.commit()

        cursor.close() 
        conn.close()

        flash('account created, Welcome {}'.format(loginpage.Username.data),"success")
        return redirect(url_for("userPrint.login"))
    return render_template("signup.html",form=loginpage)

@userPrint.route("/user/history",methods=["GET","Post"])
@login_required
def booking_history():
    if current_user.is_authenticated:
        items=[]
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("select sid,iid,quantity,trackStatus from orderlist where sid = %s",[current_user.id])
        orders=cursor.fetchall()
        for order in orders:
            cursor.execute("Select id,itemname,price,image from product where id = %s",[int(order.get("iid"))])
            tmp=cursor.fetchone()
            tmp["quantity"]=order.get("quantity")
            tmp["trackStatus"]=order.get("trackStatus")
            tmp["stackCost"]=order.get("quantity")*tmp.get("price")
            items.append(tmp.copy())
        cursor.close()
        conn.close()
        return render_template("history.html",items=items)
    else:
        flash('Login required',"info")
    return redirect(url_for('mainPrint.lnding'))
