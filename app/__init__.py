from flask import Flask
from flask_cors import CORS
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize CORS with more permissive settings for development
    CORS(app, 
         resources={r"/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"])
    
    # Initialize database
    from app.models import init_db
    init_db()
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app 