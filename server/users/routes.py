from flask import Blueprint,render_template,url_for,flash,redirect,request,session
from flask_login import login_required,login_user,logout_user,current_user
from server.users.form import loginForm, regForm
from server import mysql,bcrypt
from server.model import user
import pymysql

userPrint=Blueprint("userPrint",__name__)

@userPrint.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("mainPrint.lnding"))

@userPrint.route("/login",methods=["GET","POST"])
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

@userPrint.route("/signup",methods=["GET","POST"])
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


@userPrint.route("/add",methods=["GET","POST"])
def add():
    iid=None
    quantity=None
    if request.method=="POST":
        iid=request.form.get("id")
        quantity=request.form.get("Quantity")
    elif request.method=="GET":
        iid=request.args.get("id")
        quantity=request.args.get("Quantity")
    if iid and quantity:
        quantity=int(quantity)
        session.modified = True
        
        if "cart" in session:
            if iid in session["cart"]:
                session["cart"][iid]=quantity+session["cart"][iid]
            else:
                session["cart"][iid]=quantity
        else:
            session["cart"]={}
            session["cart"][iid]=quantity
        flash('successfully added product'.format(iid,quantity),"success")
    else:
        flash('some issue with adding product',"warning")
    print(session)
    return redirect(url_for("mainPrint.lnding"))

@userPrint.route("/showcart",methods=["GET","POST"])
def showcart():
    cart=session.get("cart")
    result=[]
    totalCost=0
    if cart:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        for strid,quantity in cart.items():
            cursor.execute("Select id,itemname,price,image from product where id = %s",[int(strid)])
            tmp=cursor.fetchone()
            tmp["quantity"]=quantity
            tmp["stackCost"]=quantity*float(tmp['price'])
            result.append(tmp.copy())
        cursor.close() 
        conn.close()
        
        for item in result:
            totalCost+=item["stackCost"]

    return render_template("cart.html",items=result,totalCost=totalCost)

# @userPrint.route("/clscart",methods=["GET","POST"])
# def clscart():
#     session.modified = True
#     session.pop("cart",None)
#     return session.get("cart") if session.get("cart") else "none"

@userPrint.route("/reset_item_count",methods=["GET","POST"])
def reset_item_count():
    iid=None
    quantity=None
    if request.method=="POST":
        print(request.form)
        iid=request.form.get("id")
        quantity=request.form.get("Quantity")
    elif request.method=="GET":
        iid=request.args.get("id")
        quantity=request.args.get("Quantity")
    if iid and quantity:
        iid=str(iid)
        quantity=int(quantity)
        session.modified = True
        if "cart" in session:
            session["cart"][iid]=quantity
        else:
            session["cart"]={}
            session["cart"][iid]=quantity
        flash('successfully changed product\'s count to {}'.format(quantity),"success")
    else:
        flash('some issue with {} or {}'.format('product','quantity'),"warning")
    return redirect(url_for("userPrint.showcart"))

@userPrint.route("/remove_item",methods=["GET","POST"])
def remove_item():
    iid=None
    if request.method=="POST":
        iid=request.form.get("id")
    elif request.method=="GET":
        iid=request.args.get("id")
    if iid:
        iid=str(iid)
        session.modified = True
        if "cart" in session:
            session["cart"].pop(str(iid))
        flash('successfully poped {} from cart'.format('product'),"success")
    else:
        flash('some issue with poping {}'.format('product'),"warning")
    return redirect(url_for("userPrint.showcart"))

@userPrint.route("/proceed_to_buy",methods=["GET","Post"])
@login_required
def proceed_to_buy():
    if current_user.is_authenticated:
        cart=session.get("cart")
        if cart:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            for strid,quantity in cart.items():
                cursor.execute("insert into orderlist (sid,iid,quantity) values ( %s,%s,%s)",[current_user.id,int(strid),quantity])
            conn.commit()
            cursor.close() 
            conn.close()
            session.pop("cart",None)
            flash('your order has been placed',"success")
        else:
            flash('your cart was empty',"info")
    else:
        flash('login please',"info")
        return redirect(url_for("userPrint.showcart"))
    return redirect(url_for("userPrint.booking_history"))

@userPrint.route("/booking_history",methods=["GET","Post"])
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

@userPrint.route("/view_user_booking",methods=["GET","Post"])
@login_required
def view_user_booking():
    if current_user.is_authenticated:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select id,is_admin from shopper where id=%s",[current_user.id])
        result=cursor.fetchone()
        cursor.close() 
        conn.close()
        if result['is_admin']== True:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("Select id,username,is_admin from shopper")
            users=cursor.fetchall()
            cursor.close() 
            conn.close()
            return render_template("viewUser.html",users=users)
        else:
            flash('requires admin login',"info")
            return redirect(url_for('mainPrint.lnding'))
    else:
        flash('Login required',"info")
        return redirect(url_for('mainPrint.lnding'))


@userPrint.route("/view_selected_user",methods=["GET","Post"])
@login_required
def view_selected_user():
    if current_user.is_authenticated:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select id,is_admin from shopper where id=%s",[current_user.id])
        result=cursor.fetchone()
        cursor.close() 
        conn.close()
        if result['is_admin']== True:
            sid=None
            if request.method=="POST":
                sid=request.form.get("sid")
            elif request.method=="GET":
                sid=request.args.get("sid")
            if sid:
                items=[]
                conn = mysql.connect()
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute("select oid,sid,iid,quantity,trackStatus from orderlist where sid = %s",[sid])
                orders=cursor.fetchall()
                for order in orders:
                    cursor.execute("Select id,itemname,price,image from product where id = %s",[int(order.get("iid"))])
                    tmp=cursor.fetchone()
                    tmp["oid"]=order.get("oid")
                    tmp["sid"]=sid
                    tmp["quantity"]=order.get("quantity")
                    tmp["trackStatus"]=order.get("trackStatus")
                    tmp["stackCost"]=order.get("quantity")*tmp.get("price")
                    items.append(tmp.copy())
                cursor.close()
                conn.close()
                return render_template("viewUserBooking.html",items=items)
            else:
                flash('no user selected',"info")
                redirect(url_for('userPrint.view_user_booking'))
        else:
            flash('requires admin login',"info")
            return redirect(url_for('userPrint.mainPrint.lnding'))
    else:
        flash('Login required',"info")
        return redirect(url_for('userPrint.mainPrint.lnding'))

@userPrint.route("/update_status",methods=["GET","Post"])
@login_required
def update_status():
    if current_user.is_authenticated:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select id,is_admin from shopper where id=%s",[current_user.id])
        result=cursor.fetchone()
        cursor.close() 
        conn.close()
        if result['is_admin']== True:
            userid=None
            prodid=None
            oid=None
            if request.method=="POST":
                userid=request.form.get("userid")
                prodid=request.form.get("prodid")
                oid=request.form.get("oid")
            elif request.method=="GET":
                userid=request.args.get("userid")
                prodid=request.args.get("prodid")
                oid=request.args.get("oid")
            if userid and prodid:
                conn = mysql.connect()
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute("select oid,sid,iid,quantity,trackStatus from orderlist where sid = %s and iid = %s and oid = %s",[userid,prodid,oid])
                order=cursor.fetchone()
                cursor.execute("update orderlist set trackStatus=%s where oid = %s",[int(order["trackStatus"])+1, int(order["oid"]) ])
                conn.commit()
                cursor.close() 
                conn.close()
                flash('Successfully updated status',"Success")
                return redirect(url_for('userPrint.view_selected_user')+"?sid={}".format(userid))
            else:
                flash('updation failed',"danger")
                return redirect(url_for('userPrint.view_user_booking'))
        else:
            flash('requires admin login',"info")
            return redirect(url_for('mainPrint.lnding'))
    else:
        flash('Login required',"info")
        return redirect(url_for('mainPrint.lnding'))