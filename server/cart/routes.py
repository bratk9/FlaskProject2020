from flask import Blueprint,render_template,url_for,flash,redirect,request,session
from server import mysql,bcrypt
from flask_login import login_required,current_user

import pymysql

cartPrint=Blueprint("cartPrint",__name__)

@cartPrint.route("/cart/add",methods=["GET","POST"])
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

@cartPrint.route("/cart/show",methods=["GET","POST"])
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


@cartPrint.route("/cart/reset",methods=["GET","POST"])
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
    return redirect(url_for("cartPrint.showcart"))

@cartPrint.route("/cart/remove",methods=["GET","POST"])
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
    return redirect(url_for("cartPrint.showcart"))

@cartPrint.route("/cart/buy",methods=["GET","Post"])
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
        return redirect(url_for("cartPrint.showcart"))
    return redirect(url_for("userPrint.booking_history"))