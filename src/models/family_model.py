"""
Family Model

Handles all database operations related to families.
Follows the thin model principle - focuses only on database interactions.
"""

import secrets
import string
from src import db


class Family(db.Model):
    """Family model for family groups."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    family_code = db.Column(db.String(10), unique=True, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    family_points = db.Column(db.Integer, default=0, nullable=False)
    
    # Relationships
    users = db.relationship('User', backref='family', lazy=True, foreign_keys='User.family_id')
    children = db.relationship('Child', backref='family', lazy=True)
    
    def to_dict(self):
        """Convert family object to dictionary.
        
        Returns:
            dict: Family data
        """
        return {
            'id': self.id,
            'name': self.name,
            'family_code': self.family_code,
            'creator_id': self.creator_id,
            'family_points': self.family_points
        }
    
    @classmethod
    def get_by_id(cls, family_id):
        """Get family by ID.
        
        Args:
            family_id (int): Family ID to search for
            
        Returns:
            Family or None: Family object if found, None otherwise
        """
        return cls.query.get(family_id)
    
    @classmethod
    def get_by_code(cls, family_code):
        """Get family by family code.
        
        Args:
            family_code (str): Family code to search for
            
        Returns:
            Family or None: Family object if found, None otherwise
        """
        return cls.query.filter_by(family_code=family_code).first()
    
    @classmethod
    def generate_unique_family_code(cls):
        """Generate a unique 6-character family code.
        
        Returns:
            str: Unique family code
        """
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            if not cls.query.filter_by(family_code=code).first():
                return code
    
    @classmethod
    def create_family(cls, name, creator_id):
        """Create a new family.
        
        Args:
            name (str): Name of the family
            creator_id (int): ID of the user creating the family
            
        Returns:
            Family: Newly created family object
        """
        family_code = cls.generate_unique_family_code()
        family = cls(name=name, family_code=family_code, creator_id=creator_id)
        db.session.add(family)
        db.session.commit()
        return family
    
    @classmethod
    def code_exists(cls, family_code):
        """Check if family code already exists.
        
        Args:
            family_code (str): Family code to check
            
        Returns:
            bool: True if code exists, False otherwise
        """
        return cls.query.filter_by(family_code=family_code).first() is not None
    
    def add_points(self, points):
        """Add points to the family point pool.
        
        Args:
            points (int): Number of points to add
        """
        if points > 0:
            self.family_points += points
            db.session.commit()
    
    def subtract_points(self, points):
        """Subtract points from the family point pool.
        
        Args:
            points (int): Number of points to subtract
            
        Returns:
            bool: True if successful, False if insufficient points
        """
        if points > 0 and self.family_points >= points:
            self.family_points -= points
            db.session.commit()
            return True
        return False
    
    def set_points(self, points):
        """Set the family point pool to a specific value.
        
        Args:
            points (int): Number of points to set
        """
        if points >= 0:
            self.family_points = points
            db.session.commit()
