from server import mysql
from flask_login import current_user,login_required,current_user
from flask import render_template,flash,redirect,url_for,Blueprint
from server.items.form import addItemForm
from server.utils import savefile
import pymysql

itemPrint=Blueprint("itemPrint",__name__,url_prefix="/shop")

@itemPrint.route("/add",methods=["GET","POST"])
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
            return redirect(url_for("mainPrint.lnding"))

    else:
        flash('login is required',"warning")
        return redirect(url_for("mainPrint.lnding"))
