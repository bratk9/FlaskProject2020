from flask import Flask
from flaskext.mysql import MySQL
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import pymysql
from server.config import Config

mysql=MySQL()
bcrypt=Bcrypt()
loginManager=LoginManager()
loginManager.login_view='login'

from server.items.routes import itemPrint
from server.main.routes import mainPrint
from server.users.routes import userPrint
from server.cart.routes import cartPrint
from server.admin.routes import adminPrint



def create_app(config_class=Config):
    app=Flask(__name__)
    app.config.from_object(Config)
    app.secret_key="a2fe316b5479facc91981d2033b9b3f6"
    app.register_blueprint(adminPrint)
    app.register_blueprint(itemPrint)
    app.register_blueprint(mainPrint)
    app.register_blueprint(userPrint)
    app.register_blueprint(cartPrint)

    mysql.init_app(app)
    bcrypt.init_app(app)
    loginManager.init_app(app)
    return app
 