import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, generate_csrf
from sqlalchemy.orm import DeclarativeBase

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Define your base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize the Flask app first
app = Flask(__name__)

# Initialize extensions after app is defined
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()

# Add your context processor now that the app is defined
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())

# Import routes after app is initialized
from routes import *



# CSRF Protection Config
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600

# Secret Key (Fallback if Environment Variable is Missing)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# MySQL Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Apple123@localhost/jewellery_inventory"

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Extensions
db.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)

# Flask-Login Configuration
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import Routes and Models After App Context is Created
with app.app_context():
    from routes import *
    import models
    db.create_all()

