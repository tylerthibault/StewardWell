"""
Configuration settings for StewardWell Flask application
"""
import os

# Application settings
APPNAME = "StewardWell"
PORT = int(os.environ.get('PORT', 5111))
HOST = os.environ.get('HOST', '127.0.0.1')

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']

# Database settings
DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///stewardwell.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Template and static folder settings
TEMPLATE_FOLDER = 'src/templates'
STATIC_FOLDER = 'src/static'