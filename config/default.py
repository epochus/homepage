"""
    config/default.py
    -----------------
    Default configuration settings

"""
import os

DEBUG = True
#DEBUG = os.environ.get('FLASK_DEBUG', False)
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')
USERNAME = os.environ.get('FLASK_USERNAME', 'admin')
SALT = os.environ.get('FLASK_SALT', 'default-pw-salt')
PASSWORD = os.environ.get('FLASK_PASSWORD', ('pbkdf2:sha1:1000$CiSKzpGa$1953516c587963ce1c26454dd141ffbf35aa7465'))

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(PROJECT_DIR, 'homepage')
DATABASE =  os.path.join(os.environ.get('OPENSHIFT_DATA_DIR', APP_DIR), 'sqlite3.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DATABASE)
HOST_NAME = os.environ.get('OPENSHIFT_APP_DNS', 'localhost')
APP_NAME = os.environ.get('OPENSHIFT_APP_NAME', 'homepage')
IP = os.environ.get('OPENSHIFT_PYTHON_IP', '127.0.0.1')
PORT = int(os.environ.get('OPENSHIFT_PYTHON_PORT', 8080))
