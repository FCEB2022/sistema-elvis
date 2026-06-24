from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    with app.app_context():
        # Ensure PostgreSQL schema exists if using Postgres
        if db.engine.url.drivername.startswith('postgres'):
            db.session.execute(db.text("CREATE SCHEMA IF NOT EXISTS elvis;"))
            db.session.commit()
        db.create_all()

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app

