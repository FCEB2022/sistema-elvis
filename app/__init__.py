from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import logging

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    with app.app_context():
        try:
            # Import models to register them with metadata
            from app import models
            # Ensure PostgreSQL schema exists if using Postgres
            if db.engine.url.drivername.startswith('postgres'):
                db.session.execute(db.text("CREATE SCHEMA IF NOT EXISTS elvis;"))
                db.session.commit()
            db.create_all()
            logging.info("Database tables created successfully.")
        except Exception as e:
            logging.error(f"Error setting up database: {e}")
            # Don't raise — let the app start, routes will handle DB errors gracefully

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app


