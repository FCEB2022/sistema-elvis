import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_sistema_elvis_aslyon'
    
    # Render provides postgres://, but SQLAlchemy requires postgresql://
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
        
    if db_url and 'postgresql' in db_url:
        if 'search_path' not in db_url:
            if '?' in db_url:
                db_url += '&options=-csearch_path%3Delvis'
            else:
                db_url += '?options=-csearch_path%3Delvis'
                
    SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///sistema_elvis.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


