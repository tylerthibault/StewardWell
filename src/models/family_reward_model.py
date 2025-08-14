"""
Family Reward Model

Handles all database operations related to family rewards (bought with points).
Follows the thin model principle - focuses only on database interactions.
"""

from datetime import datetime
from src import db


class FamilyReward(db.Model):
    """Family reward model for rewards purchased with points."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    qty = db.Column(db.Integer, default=1, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    point_cost = db.Column(db.Integer, nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    family = db.relationship('Family', backref='family_rewards')
    creator = db.relationship('User', backref='created_family_rewards')
    
    def to_dict(self):
        """Convert family reward object to dictionary.
        
        Returns:
            dict: Family reward data
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'qty': self.qty,
            'is_available': self.is_available,
            'point_cost': self.point_cost,
            'family_id': self.family_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_id(cls, reward_id):
        """Get family reward by ID.
        
        Args:
            reward_id (int): Family reward ID to search for
            
        Returns:
            FamilyReward or None: Family reward object if found, None otherwise
        """
        return cls.query.get(reward_id)
    
    @classmethod
    def get_by_family(cls, family_id, available_only=False):
        """Get all family rewards in a family.
        
        Args:
            family_id (int): Family ID to search for
            available_only (bool): If True, only return available rewards
            
        Returns:
            list: List of FamilyReward objects
        """
        query = cls.query.filter_by(family_id=family_id)
        if available_only:
            query = query.filter_by(is_available=True)
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def create_reward(cls, name, point_cost, family_id, created_by, description=None, qty=1, is_available=True):
        """Create a new family reward.
        
        Args:
            name (str): Name of the reward
            point_cost (int): Cost in points
            family_id (int): ID of the family
            created_by (int): ID of the user creating the reward
            description (str, optional): Description of the reward
            qty (int, optional): Quantity available, defaults to 1
            is_available (bool, optional): Whether the reward is available, defaults to True
            
        Returns:
            FamilyReward: Newly created family reward object
        """
        reward = cls(
            name=name,
            description=description,
            qty=qty,
            is_available=is_available,
            point_cost=point_cost,
            family_id=family_id,
            created_by=created_by
        )
        db.session.add(reward)
        db.session.commit()
        return reward
    
    def update(self, **kwargs):
        """Update the family reward with provided fields.
        
        Args:
            **kwargs: Fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def delete(self):
        """Delete this family reward from the database."""
        db.session.delete(self)
        db.session.commit()