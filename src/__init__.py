"""
StewardWell Application Factory

This module initializes the Flask application and sets up all extensions.
Following the application factory pattern for better testability and configuration management.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app(config_object=None):
    """Create and configure the Flask application.
    
    Args:
        config_object: Optional configuration object to override defaults
        
    Returns:
        Flask: Configured Flask application instance
    """
    # Get absolute paths for templates and static files
    src_dir = os.path.dirname(os.path.abspath(__file__))
    template_folder = os.path.join(src_dir, 'templates')
    static_folder = os.path.join(src_dir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_folder, 
                static_folder=static_folder)
    
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config['SECRET_KEY'] = config.SECRET_KEY
        app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Import and register blueprints
    from src.controllers.auth_controller import auth_bp
    from src.controllers.family_controller import family_bp
    from src.controllers.child_controller import child_bp
    from src.controllers.user_controller import user_bp
    from src.controllers.main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(child_bp)
    app.register_blueprint(user_bp)
    
    # Set up user loader for Flask-Login
    from src.models.user_model import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))
    
    return app
