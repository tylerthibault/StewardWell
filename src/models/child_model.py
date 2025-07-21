"""
Child Model

Handles all database operations related to children.
Follows the thin model principle - focuses only on database interactions.
"""

from src import db


class Child(db.Model):
    """Child model for child accounts within families."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def to_dict(self):
        """Convert child object to dictionary.
        
        Returns:
            dict: Child data
        """
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
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
    def create_child(cls, name, family_id, created_by, age=None):
        """Create a new child.
        
        Args:
            name (str): Name of the child
            family_id (int): ID of the family
            created_by (int): ID of the user creating the child
            age (int, optional): Age of the child
            
        Returns:
            Child: Newly created child object
        """
        child = cls(name=name, family_id=family_id, created_by=created_by, age=age)
        db.session.add(child)
        db.session.commit()
        return child
    
    def delete(self):
        """Delete this child from the database."""
        db.session.delete(self)
        db.session.commit()
