"""
    homepage/__init__.py
    --------------------
    Initialization of Flask application
"""
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.misaka import Misaka

# Create application object
app = Flask(__name__, instance_relative_config=True)

# Load default configuration
app.config.from_object('config.default')

# Wrap Flask instance with Flask-Misaka
Misaka(app)

# Load non-VC configurations from instance folder
# app.config.from_pyfile('instance.cfg', silent=True)

# Load configurations specified by APP_SETTINGS environment variable
# Variables defined here will override default configurations
# app.config.from_envvar('APP_SETTINGS', silent=True)

# Initialize database
db = SQLAlchemy(app)

if app.debug:
    from werkzeug.debug import DebuggedApplication
    app.wsgi_app = DebuggedApplication(app.wsgi_app, True)


# Import views
from homepage import views
# Import admin
from homepage import admin
