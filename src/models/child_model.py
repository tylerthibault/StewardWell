"""
Child Model

Handles all database operations related to children.
Follows the thin model principle - focuses only on database interactions.
"""

from datetime import date
from src import db


class Child(db.Model):
    """Child model for child accounts within families."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)  # Keep for backward compatibility
    birthdate = db.Column(db.Date, nullable=True)
    pin = db.Column(db.String(10), nullable=True)  # Child's PIN for access
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def calculate_age(self):
        """Calculate age from birthdate.
        
        Returns:
            int or None: Calculated age, or None if no birthdate
        """
        if not self.birthdate:
            return self.age  # Fallback to stored age
        
        today = date.today()
        age = today.year - self.birthdate.year
        
        # Adjust if birthday hasn't occurred this year yet
        if today.month < self.birthdate.month or (today.month == self.birthdate.month and today.day < self.birthdate.day):
            age -= 1
            
        return age
    
    def to_dict(self):
        """Convert child object to dictionary.
        
        Returns:
            dict: Child data
        """
        return {
            'id': self.id,
            'name': self.name,
            'age': self.calculate_age(),
            'birthdate': self.birthdate.isoformat() if self.birthdate else None,
            'pin': self.pin,
            'family_id': self.family_id,
            'created_by': self.created_by
        }
    
    @classmethod
    def get_by_id(cls, child_id):
        """Get child by ID.
        
        Args:
            child_id (int): Child ID to search for
            
        Returns:
            Child or None: Child object if found, None otherwise
        """
        return cls.query.get(child_id)
    
    @classmethod
    def get_by_family(cls, family_id):
        """Get all children in a family.
        
        Args:
            family_id (int): Family ID to search for
            
        Returns:
            list: List of Child objects
        """
        return cls.query.filter_by(family_id=family_id).all()
    
    @classmethod
    def create_child(cls, name, family_id, created_by, age=None, birthdate=None, pin=None):
        """Create a new child.
        
        Args:
            name (str): Name of the child
            family_id (int): ID of the family
            created_by (int): ID of the user creating the child
            age (int, optional): Age of the child (for backward compatibility)
            birthdate (date, optional): Birthdate of the child
            pin (str, optional): PIN for the child
            
        Returns:
            Child: Newly created child object
        """
        child = cls(name=name, family_id=family_id, created_by=created_by, 
                   age=age, birthdate=birthdate, pin=pin)
        db.session.add(child)
        db.session.commit()
        return child
    
    def update(self, name=None, birthdate=None, pin=None, age=None):
        """Update child information.
        
        Args:
            name (str, optional): New name
            birthdate (date, optional): New birthdate  
            pin (str, optional): New PIN
            age (int, optional): New age (for backward compatibility)
        """
        if name is not None:
            self.name = name
        if birthdate is not None:
            self.birthdate = birthdate
        if pin is not None:
            self.pin = pin
        if age is not None:
            self.age = age
        db.session.commit()
    
    def delete(self):
        """Delete this child from the database."""
        db.session.delete(self)
        db.session.commit()
