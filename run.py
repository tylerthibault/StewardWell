"""
StewardWell Production Server

Production entry point for the StewardWell application.
Uses the proper MVC structure with application factory pattern.
"""

from src import create_app, db
import config

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Production mode - run without debug
    with app.app_context():
        # Import models to ensure they are registered
        from src.models import main as models
        db.create_all()
    
    print(f"Starting {config.APPNAME} in production mode...")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
