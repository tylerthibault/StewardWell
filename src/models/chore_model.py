"""
Chore Model

Handles all database operations related to chores.
Follows the thin model principle - focuses only on database interactions.
"""

import json
from datetime import datetime
from src import db


class Chore(db.Model):
    """Chore model for family chores."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    coin_amount = db.Column(db.Integer, default=0, nullable=False)
    point_amount = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_recurring = db.Column(db.Boolean, default=False, nullable=False)
    recurring_days = db.Column(db.Text, nullable=True)  # JSON string of day numbers (0=Monday, 6=Sunday)
    assigned_child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=True)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, completed, expired
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), default='medium', nullable=False)  # low, medium, high
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    assigned_child = db.relationship('Child', backref='chores', lazy=True)
    assigned_user = db.relationship('User', backref='assigned_chores', lazy=True, foreign_keys=[assigned_user_id])
    creator = db.relationship('User', backref='created_chores', lazy=True, foreign_keys=[created_by])
    
    def to_dict(self):
        """Convert chore object to dictionary.
        
        Returns:
            dict: Chore data
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'coin_amount': self.coin_amount,
            'point_amount': self.point_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_recurring': self.is_recurring,
            'recurring_days': self.get_recurring_days(),
            'assigned_child_id': self.assigned_child_id,
            'assigned_user_id': self.assigned_user_id,
            'family_id': self.family_id,
            'status': self.status,
            'is_available': self.is_available,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'notes': self.notes,
            'priority': self.priority,
            'created_by': self.created_by
        }
    
    def get_recurring_days(self):
        """Get recurring days as a list of integers.
        
        Returns:
            list: List of day numbers (0=Monday, 6=Sunday) or empty list
        """
        if not self.recurring_days:
            return []
        try:
            return json.loads(self.recurring_days)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_recurring_days(self, days):
        """Set recurring days from a list of integers.
        
        Args:
            days (list): List of day numbers (0=Monday, 6=Sunday)
        """
        if days:
            self.recurring_days = json.dumps(days)
        else:
            self.recurring_days = None
    
    @classmethod
    def get_by_id(cls, chore_id):
        """Get chore by ID.
        
        Args:
            chore_id (int): Chore ID to search for
            
        Returns:
            Chore or None: Chore object if found, None otherwise
        """
        return cls.query.get(chore_id)
    
    @classmethod
    def get_by_family(cls, family_id):
        """Get all chores in a family.
        
        Args:
            family_id (int): Family ID to search for
            
        Returns:
            list: List of Chore objects
        """
        return cls.query.filter_by(family_id=family_id).all()
    
    @classmethod
    def get_by_child(cls, child_id):
        """Get all chores assigned to a child.
        
        Args:
            child_id (int): Child ID to search for
            
        Returns:
            list: List of Chore objects
        """
        return cls.query.filter_by(assigned_child_id=child_id).all()
    
    @classmethod
    def get_available_for_family(cls, family_id):
        """Get all available chores in a family.
        
        Args:
            family_id (int): Family ID to search for
            
        Returns:
            list: List of available Chore objects
        """
        return cls.query.filter_by(family_id=family_id, is_available=True).all()
    
    @classmethod
    def create_chore(cls, name, family_id, created_by, description=None, coin_amount=0, 
                     point_amount=0, is_recurring=False, recurring_days=None, 
                     assigned_child_id=None, assigned_user_id=None, due_date=None, notes=None, priority='medium'):
        """Create a new chore.
        
        Args:
            name (str): Name of the chore
            family_id (int): ID of the family
            created_by (int): ID of the user creating the chore
            description (str, optional): Description of the chore
            coin_amount (int, optional): Individual reward amount
            point_amount (int, optional): Family reward amount
            is_recurring (bool, optional): Whether chore recurs
            recurring_days (list, optional): List of day numbers for recurring
            assigned_child_id (int, optional): ID of assigned child
            assigned_user_id (int, optional): ID of assigned user (adult)
            due_date (datetime, optional): Due date for the chore
            notes (str, optional): Additional notes
            priority (str, optional): Priority level
            
        Returns:
            Chore: Newly created chore object
        """
        chore = cls(
            name=name,
            family_id=family_id,
            created_by=created_by,
            description=description,
            coin_amount=coin_amount,
            point_amount=point_amount,
            is_recurring=is_recurring,
            assigned_child_id=assigned_child_id,
            assigned_user_id=assigned_user_id,
            due_date=due_date,
            notes=notes,
            priority=priority
        )
        
        if recurring_days:
            chore.set_recurring_days(recurring_days)
        
        db.session.add(chore)
        db.session.commit()
        return chore
    
    def update_chore(self, **kwargs):
        """Update chore fields.
        
        Args:
            **kwargs: Fields to update
        """
        for key, value in kwargs.items():
            if key == 'recurring_days':
                self.set_recurring_days(value)
            elif hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def delete(self):
        """Delete this chore from the database."""
        db.session.delete(self)
        db.session.commit()
    
    def complete(self):
        """Mark this chore as completed."""
        self.status = 'completed'
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def assign_to_child(self, child_id):
        """Assign this chore to a child.
        
        Args:
            child_id (int): ID of the child to assign to
        """
        self.assigned_child_id = child_id
        self.assigned_user_id = None  # Clear user assignment
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def assign_to_user(self, user_id):
        """Assign this chore to a user (adult).
        
        Args:
            user_id (int): ID of the user to assign to
        """
        self.assigned_user_id = user_id
        self.assigned_child_id = None  # Clear child assignment
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def get_by_user(cls, user_id):
        """Get all chores assigned to a user (adult).
        
        Args:
            user_id (int): User ID to search for
            
        Returns:
            list: List of Chore objects
        """
        return cls.query.filter_by(assigned_user_id=user_id).all()
    
    def get_assigned_to(self):
        """Get who the chore is assigned to.
        
        Returns:
            dict: Information about assignment (type and name)
        """
        if self.assigned_child_id and self.assigned_child:
            return {
                'type': 'child',
                'id': self.assigned_child_id,
                'name': self.assigned_child.name
            }
        elif self.assigned_user_id and self.assigned_user:
            return {
                'type': 'user',
                'id': self.assigned_user_id,
                'name': self.assigned_user.username
            }
        else:
            return {
                'type': 'unassigned',
                'id': None,
                'name': 'Unassigned'
            }