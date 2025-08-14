"""
Individual Reward Model

Handles all database operations related to individual rewards (bought with coins).
Follows the thin model principle - focuses only on database interactions.
"""

from datetime import datetime
from src import db


class IndividualReward(db.Model):
    """Individual reward model for rewards purchased with coins."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    qty = db.Column(db.Integer, default=1, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    coin_cost = db.Column(db.Integer, nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    family = db.relationship('Family', backref='individual_rewards')
    creator = db.relationship('User', backref='created_individual_rewards')
    
    def to_dict(self):
        """Convert individual reward object to dictionary.
        
        Returns:
            dict: Individual reward data
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'qty': self.qty,
            'is_available': self.is_available,
            'coin_cost': self.coin_cost,
            'family_id': self.family_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_id(cls, reward_id):
        """Get individual reward by ID.
        
        Args:
            reward_id (int): Individual reward ID to search for
            
        Returns:
            IndividualReward or None: Individual reward object if found, None otherwise
        """
        return cls.query.get(reward_id)
    
    @classmethod
    def get_by_family(cls, family_id, available_only=False):
        """Get all individual rewards in a family.
        
        Args:
            family_id (int): Family ID to search for
            available_only (bool): If True, only return available rewards
            
        Returns:
            list: List of IndividualReward objects
        """
        query = cls.query.filter_by(family_id=family_id)
        if available_only:
            query = query.filter_by(is_available=True)
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def create_reward(cls, name, coin_cost, family_id, created_by, description=None, qty=1, is_available=True):
        """Create a new individual reward.
        
        Args:
            name (str): Name of the reward
            coin_cost (int): Cost in coins
            family_id (int): ID of the family
            created_by (int): ID of the user creating the reward
            description (str, optional): Description of the reward
            qty (int, optional): Quantity available, defaults to 1
            is_available (bool, optional): Whether the reward is available, defaults to True
            
        Returns:
            IndividualReward: Newly created individual reward object
        """
        reward = cls(
            name=name,
            description=description,
            qty=qty,
            is_available=is_available,
            coin_cost=coin_cost,
            family_id=family_id,
            created_by=created_by
        )
        db.session.add(reward)
        db.session.commit()
        return reward
    
    def update(self, **kwargs):
        """Update the individual reward with provided fields.
        
        Args:
            **kwargs: Fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def delete(self):
        """Delete this individual reward from the database."""
        db.session.delete(self)
        db.session.commit()