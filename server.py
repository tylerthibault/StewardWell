"""
StewardWell Development Server

This file is used for development. In production, use run.py instead.
Now uses the proper MVC structure with application factory pattern.
"""

from src import create_app, db
import config

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Development mode - run with debug enabled
    with app.app_context():
        # Import models to ensure they are registered
        from src.models import main as models
        db.create_all()
    
    print(f"Starting {config.APPNAME} in development mode...")
    app.run(host=config.HOST, port=config.PORT, debug=True)
