"""
Configuration de l'application
"""
import os

class Config:
    """Configuration de base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///sentinel_senior.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    # Pour la production, utilisez une base de données PostgreSQL ou MySQL
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
