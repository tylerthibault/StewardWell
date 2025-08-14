"""
Chore Model

Handles database operations for chores that can be assigned to family members.
"""

from datetime import datetime
from src import db


class Chore(db.Model):
    """Chore model for tasks assigned to family members."""
    
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    points_reward = db.Column(db.Integer, nullable=False, default=0)
    assigned_to_type = db.Column(db.String(10), nullable=False)  # 'child', 'adult', 'any'
    assigned_to_id = db.Column(db.Integer, nullable=True)  # child_id or user_id if specific assignment
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, completed, archived
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    completed_by_type = db.Column(db.String(10), nullable=True)  # 'child', 'adult'
    completed_by_id = db.Column(db.Integer, nullable=True)  # actual completer id
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    family = db.relationship('Family', backref='chores', lazy=True)
    creator = db.relationship('User', backref='created_chores', lazy=True)
    
    def to_dict(self):
        """Convert chore to dictionary."""
        return {
            'id': self.id,
            'family_id': self.family_id,
            'name': self.name,
            'description': self.description,
            'points_reward': self.points_reward,
            'assigned_to_type': self.assigned_to_type,
            'assigned_to_id': self.assigned_to_id,
            'status': self.status,
            'created_by': self.created_by,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'completed_by_type': self.completed_by_type,
            'completed_by_id': self.completed_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_by_id(cls, chore_id):
        """Get chore by ID."""
        return cls.query.get(chore_id)
    
    @classmethod
    def get_by_family(cls, family_id, status='pending'):
        """Get chores for a family."""
        if status:
            return cls.query.filter_by(family_id=family_id, status=status).all()
        return cls.query.filter_by(family_id=family_id).all()
    
    @classmethod
    def get_assigned_to_child(cls, family_id, child_id, status='pending'):
        """Get chores assigned to a specific child."""
        query = cls.query.filter_by(
            family_id=family_id,
            assigned_to_type='child',
            assigned_to_id=child_id
        )
        if status:
            query = query.filter_by(status=status)
        return query.all()
    
    @classmethod
    def get_assigned_to_adult(cls, family_id, user_id, status='pending'):
        """Get chores assigned to a specific adult."""
        query = cls.query.filter_by(
            family_id=family_id,
            assigned_to_type='adult',
            assigned_to_id=user_id
        )
        if status:
            query = query.filter_by(status=status)
        return query.all()
    
    @classmethod
    def get_available_for_anyone(cls, family_id, status='pending'):
        """Get chores that anyone can complete."""
        query = cls.query.filter_by(
            family_id=family_id,
            assigned_to_type='any'
        )
        if status:
            query = query.filter_by(status=status)
        return query.all()
    
    @classmethod
    def create_chore(cls, family_id, name, description, points_reward, 
                    assigned_to_type, created_by, assigned_to_id=None, due_date=None):
        """Create a new chore."""
        chore = cls(
            family_id=family_id,
            name=name,
            description=description,
            points_reward=points_reward,
            assigned_to_type=assigned_to_type,
            assigned_to_id=assigned_to_id,
            created_by=created_by,
            due_date=due_date
        )
        db.session.add(chore)
        db.session.commit()
        return chore
    
    def complete_chore(self, completed_by_type, completed_by_id):
        """Mark chore as completed."""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        self.completed_by_type = completed_by_type
        self.completed_by_id = completed_by_id
        db.session.commit()
        return True
    
    def archive_chore(self):
        """Archive this chore."""
        self.status = 'archived'
        db.session.commit()
    
    def update_chore(self, **kwargs):
        """Update chore fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
    
    def get_assigned_name(self):
        """Get the name of who this chore is assigned to."""
        if self.assigned_to_type == 'any':
            return 'Anyone'
        elif self.assigned_to_type == 'child' and self.assigned_to_id:
            from src.models.child_model import Child
            child = Child.get_by_id(self.assigned_to_id)
            return child.name if child else 'Unknown Child'
        elif self.assigned_to_type == 'adult' and self.assigned_to_id:
            from src.models.user_model import User
            user = User.get_by_id(self.assigned_to_id)
            return user.username if user else 'Unknown Adult'
        return 'Unassigned'