import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # Database configuration
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'orders.db')
    
    # Application configuration
    DEBUG = True
    TESTING = False 