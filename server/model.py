from server import loginManager,mysql
from flask_login import UserMixin
import pymysql

@loginManager.user_loader
def load_user(user_id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("Select username,id,pword,is_admin from shopper where id=%s",[int(user_id)])
    result=cursor.fetchone()
    cursor.close() 
    conn.close()
    return user(result["username"],result["id"],result["is_admin"])

@loginManager.user_loader
def load_user(user_id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("Select username,id,pword,is_admin from shopper where id=%s",[int(user_id)])
    result=cursor.fetchone()
    cursor.close() 
    conn.close()
    return user(result["username"],result["id"],result["is_admin"])

class user(UserMixin):
    def __init__(self,username,id,is_admin):
        super().__init__()
        self.username=username
        self.id=id
        self.is_admin=is_admin