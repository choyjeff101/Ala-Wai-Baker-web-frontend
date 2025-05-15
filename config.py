import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # Database configuration
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'orders.db')
    
    # Application configuration
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    # Production-specific settings
    DEBUG = False
    TESTING = False
    
    # Use environment variables for sensitive data
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database configuration for production
    DATABASE = os.environ.get('DATABASE_URL', Config.DATABASE) 