from server import mysql
import os
from flask import current_app
import pymysql

def savefile(filedata):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("Select max(id) as last from product")
    result=cursor.fetchone()
    cursor.close() 
    conn.close()

    uploade_filename,file_extension=os.path.splitext(filedata.filename)
    save_file_name=str(int(result["last"])+1)+file_extension

    filedata.save(os.path.join(current_app.root_path,'static','images','shoes',save_file_name))
    return os.path.join('shoes',save_file_name)