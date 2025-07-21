"""
User Model

Handles all database operations related to users.
Follows the thin model principle - focuses only on database interactions.
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from src import db


class User(UserMixin, db.Model):
    """User model for parent accounts."""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=True)
    
    def set_password(self, password):
        """Hash and set the user's password.
        
        Args:
            password (str): Plain text password to hash
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches stored hash.
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary.
        
        Returns:
            dict: User data excluding sensitive information
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'family_id': self.family_id
        }
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID.
        
        Args:
            user_id (int): User ID to search for
            
        Returns:
            User or None: User object if found, None otherwise
        """
        return cls.query.get(user_id)
    
    @classmethod
    def get_by_username(cls, username):
        """Get user by username.
        
        Args:
            username (str): Username to search for
            
        Returns:
            User or None: User object if found, None otherwise
        """
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email.
        
        Args:
            email (str): Email to search for
            
        Returns:
            User or None: User object if found, None otherwise
        """
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def create_user(cls, username, email, password):
        """Create a new user.
        
        Args:
            username (str): Unique username
            email (str): Unique email address
            password (str): Plain text password (will be hashed)
            
        Returns:
            User: Newly created user object
        """
        user = cls(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @classmethod
    def username_exists(cls, username):
        """Check if username already exists.
        
        Args:
            username (str): Username to check
            
        Returns:
            bool: True if username exists, False otherwise
        """
        return cls.query.filter_by(username=username).first() is not None
    
    @classmethod
    def email_exists(cls, email):
        """Check if email already exists.
        
        Args:
            email (str): Email to check
            
        Returns:
            bool: True if email exists, False otherwise
        """
        return cls.query.filter_by(email=email).first() is not None
    
    def update_family(self, family_id):
        """Update user's family association.
        
        Args:
            family_id (int): ID of the family to join
        """
        self.family_id = family_id
        db.session.commit()
