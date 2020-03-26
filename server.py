from flask import Flask,render_template,flash,redirect,url_for,request,session
from flaskext.mysql import MySQL
from form import loginForm,regForm,addItemForm
from flask_bcrypt import Bcrypt
from flask_login import UserMixin,login_user,logout_user,LoginManager,current_user,login_required
import os

import pymysql

app=Flask(__name__)
app.secret_key="a2fe316b5479facc91981d2033b9b3f6"

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'shop'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql=MySQL(app)
bcrypt=Bcrypt(app)
loginManager=LoginManager(app)
loginManager.login_view='login'

class user(UserMixin):
    def __init__(self,username,id,is_admin):
        super().__init__()
        self.username=username
        self.id=id
        self.is_admin=is_admin


@loginManager.user_loader
def load_user(user_id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("Select username,id,pword,is_admin from shopper where id=%s",[int(user_id)])
    result=cursor.fetchone()
    cursor.close() 
    conn.close()
    return user(result["username"],result["id"],result["is_admin"])




@app.route("/")
@app.route("/home")
def lnding():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("Select * from product")
    result=cursor.fetchall()
    cursor.close() 
    conn.close()
    return render_template("home.html",products=result)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("lnding"))

@app.route("/login",methods=["GET","POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("lnding"))

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
            
            return redirect(next_pg) if next_pg else redirect(url_for("lnding"))
        else:
            flash('login failed for {}. Make sure you are signed up.'.format(loginpage.Username.data),"warning")
        
    return render_template("Login.html",form=loginpage)

@app.route("/signup",methods=["GET","POST"])
def signup():

    if current_user.is_authenticated:
        return redirect(url_for("lnding"))

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
        return redirect(url_for("lnding"))
    return render_template("signup.html",form=loginpage)

def savefile(filedata):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("Select count(*) as last from product")
    result=cursor.fetchone()
    cursor.close() 
    conn.close()

    uploade_filename,file_extension=os.path.splitext(filedata.filename)
    save_file_name=str(int(result["last"])+1)+file_extension

    filedata.save(os.path.join(app.root_path,'static','images','shoes',save_file_name))
    return os.path.join('shoes',save_file_name)

@app.route("/addProduct",methods=["GET","POST"])
@login_required
def addProduct():
    if current_user.is_authenticated:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select id,is_admin from shopper where id=%s",[current_user.id])
        result=cursor.fetchone()
        cursor.close() 
        conn.close()
        if result['is_admin']== True:
            addProduct=addItemForm()
            if addProduct.validate_on_submit():
                Itm_name=addProduct.Item_Name.data
                price=addProduct.Price.data
                filename=savefile(addProduct.Picture.data)

                conn = mysql.connect()
                cursor = conn.cursor()

                cursor.execute("insert into product (itemname,image,price) value (%s,%s,%s)",[Itm_name,filename,price])
                conn.commit()

                cursor.close() 
                conn.close()

                print(Itm_name,price,filename)

                flash('new product added',"success")
            return render_template("addProduct.html",form=addProduct)

        else:
            flash('You are not an admin. Please use an admin account',"danger")
            return redirect(url_for("lnding"))

    else:
        flash('login is required',"warning")
        return redirect(url_for("lnding"))

@app.route("/add",methods=["GET","POST"])
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
        flash('successfully added {}, quantity {}'.format(iid,quantity),"success")
    else:
        flash('some issue with {} or {}'.format(iid,quantity),"warning")
    print(session)
    return redirect(url_for("lnding"))

@app.route("/showcart",methods=["GET","POST"])
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

# @app.route("/clscart",methods=["GET","POST"])
# def clscart():
#     session.modified = True
#     session.pop("cart",None)
#     return session.get("cart") if session.get("cart") else "none"

@app.route("/reset_item_count",methods=["GET","POST"])
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
        flash('successfully changed {}\'s count to {}'.format(iid,quantity),"success")
    else:
        flash('some issue with {} or {}'.format(iid,quantity),"warning")
    return redirect(url_for("showcart"))

@app.route("/remove_item",methods=["GET","POST"])
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
        flash('successfully poped {}'.format(iid),"success")
    else:
        flash('some issue with {}'.format(iid),"warning")
    return redirect(url_for("showcart"))

@app.route("/proceed_to_buy",methods=["GET","Post"])
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
    return redirect(url_for("showcart"))

@app.route("/booking_history",methods=["GET","Post"])
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
    return redirect(url_for('lnding'))

@app.route("/view_user_booking",methods=["GET","Post"])
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
            return redirect(url_for('lnding'))
    else:
        flash('Login required',"info")
        return redirect(url_for('lnding'))


@app.route("/view_selected_user",methods=["GET","Post"])
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
                cursor.execute("select sid,iid,quantity,trackStatus from orderlist where sid = %s",[sid])
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
                return render_template("viewUserBooking.html",items=items)
            else:
                flash('no user selected',"info")
                redirect(url_for('view_user_booking'))
        else:
            flash('requires admin login',"info")
            return redirect(url_for('lnding'))
    else:
        flash('Login required',"info")
        return redirect(url_for('lnding'))


if __name__ == "__main__":
    app.run(debug=True)