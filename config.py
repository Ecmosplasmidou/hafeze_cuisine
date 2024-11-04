import os

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/hafeze_cuisine'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Correction de la faute de frappe
    DEBUG = True
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'app/static')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'hafeze59@hotmail.com'
    MAIL_PASSWORD = 'hafeze59'