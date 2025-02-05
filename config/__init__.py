import os

# MySQL Configuration
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Root@123'
MYSQL_DB = 'virtual_wardrobe'
MYSQL_CURSORCLASS = 'DictCursor'

# Secret Key for Security
SECRET_KEY = 'supersecretkey'  # Change this for production

# Session Configuration
SESSION_TYPE = 'filesystem'

# Create Uploads Directory if Not Exists
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
