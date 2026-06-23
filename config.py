import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_sistema_elvis_aslyon'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///sistema_elvis.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
