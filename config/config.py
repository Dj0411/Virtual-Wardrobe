from flask import Flask
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_session import Session
import os

app = Flask(__name__)

# 🔹 MySQL Database Configuration
app.config['MYSQL_HOST'] = 'localhost'  
app.config['MYSQL_USER'] = 'root'  
app.config['MYSQL_PASSWORD'] = 'Root@123'
app.config['MYSQL_DB'] = 'virtual_wardrobe'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#  Secret Key for Security
app.config['SECRET_KEY'] = 'supersecretkey'  # Change this for production

#  Session Configuration
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

#  Initialize MySQL & Bcrypt
mysql = MySQL(app)
bcrypt = Bcrypt(app)


#Create Uploads Directory if Not Exists
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
