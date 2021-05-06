from flask import Blueprint,render_template,url_for,flash,redirect,request,session
from flask_login import login_required,current_user
from server import mysql

import pymysql

adminPrint=Blueprint("adminPrint", __name__)

@adminPrint.route("/admin/user/show-all",methods=["GET","Post"])
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


@adminPrint.route("/admin/user/show-specific",methods=["GET","Post"])
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
                redirect(url_for('adminPrint.view_user_booking'))
        else:
            flash('requires admin login',"info")
            return redirect(url_for('mainPrint.lnding'))
    else:
        flash('Login required',"info")
        return redirect(url_for('mainPrint.lnding'))

@adminPrint.route("/admin/user/update-order",methods=["GET","Post"])
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
                return redirect(url_for('adminPrint.view_selected_user')+"?sid={}".format(userid))
            else:
                flash('updation failed',"danger")
                return redirect(url_for('adminPrint.view_user_booking'))
        else:
            flash('requires admin login',"info")
            return redirect(url_for('mainPrint.lnding'))
    else:
        flash('Login required',"info")
        return redirect(url_for('mainPrint.lnding'))