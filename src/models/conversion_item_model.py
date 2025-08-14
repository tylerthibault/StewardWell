"""
Conversion Item Model

Handles all database operations related to coin-to-points conversion items.
Follows the thin model principle - focuses only on database interactions.
"""

from datetime import datetime
from src import db


class ConversionItem(db.Model):
    """Conversion item model for coin-to-points conversions."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    coin_cost = db.Column(db.Integer, nullable=False)  # Cost in coins
    points_value = db.Column(db.Integer, nullable=False)  # Points received
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    family = db.relationship('Family', backref='conversion_items')
    creator = db.relationship('User', backref='created_conversion_items')
    
    def to_dict(self):
        """Convert conversion item object to dictionary.
        
        Returns:
            dict: Conversion item data
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'coin_cost': self.coin_cost,
            'points_value': self.points_value,
            'is_available': self.is_available,
            'family_id': self.family_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_id(cls, item_id):
        """Get conversion item by ID.
        
        Args:
            item_id (int): Conversion item ID to search for
            
        Returns:
            ConversionItem or None: Conversion item object if found, None otherwise
        """
        return cls.query.get(item_id)
    
    @classmethod
    def get_by_family(cls, family_id, available_only=False):
        """Get all conversion items in a family.
        
        Args:
            family_id (int): Family ID to search for
            available_only (bool): If True, only return available items
            
        Returns:
            list: List of ConversionItem objects
        """
        query = cls.query.filter_by(family_id=family_id)
        if available_only:
            query = query.filter_by(is_available=True)
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def create_item(cls, name, coin_cost, points_value, family_id, created_by, description=None, is_available=True):
        """Create a new conversion item.
        
        Args:
            name (str): Name of the conversion item
            coin_cost (int): Cost in coins
            points_value (int): Points received for conversion
            family_id (int): ID of the family
            created_by (int): ID of the user creating the item
            description (str, optional): Description of the item
            is_available (bool, optional): Whether the item is available, defaults to True
            
        Returns:
            ConversionItem: Newly created conversion item object
        """
        item = cls(
            name=name,
            description=description,
            coin_cost=coin_cost,
            points_value=points_value,
            is_available=is_available,
            family_id=family_id,
            created_by=created_by
        )
        db.session.add(item)
        db.session.commit()
        return item
    
    def update(self, **kwargs):
        """Update the conversion item with provided fields.
        
        Args:
            **kwargs: Fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def delete(self):
        """Delete this conversion item from the database."""
        db.session.delete(self)
        db.session.commit()
    
    def get_conversion_ratio(self):
        """Get the conversion ratio as a formatted string.
        
        Returns:
            str: Conversion ratio (e.g., "10 coins = 5 points")
        """
        return f"{self.coin_cost} coins = {self.points_value} points"