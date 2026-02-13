from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sentinel_senior.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Enregistrer les blueprints
    from .routes import main
    from .api import api_bp
    app.register_blueprint(main)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Importer les modèles pour créer les tables
    from . import models
    
    # Créer les tables
    with app.app_context():
        db.create_all()
    
    return app
