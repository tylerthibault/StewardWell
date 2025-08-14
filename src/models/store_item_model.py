"""
Store Item Model

Handles database operations for family store items including rewards and coins-to-points conversions.
"""

from datetime import datetime
from src import db


class StoreItem(db.Model):
    """Store item model for family store rewards and conversions."""
    
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cost = db.Column(db.Integer, nullable=False)  # Cost in points
    quantity = db.Column(db.Integer, nullable=True)  # null = infinite
    item_type = db.Column(db.String(20), nullable=False, default='reward')  # reward, coins_to_points
    conversion_ratio = db.Column(db.Integer, nullable=True)  # For coins_to_points items: coins per point
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    family = db.relationship('Family', backref='store_items', lazy=True)
    creator = db.relationship('User', backref='created_store_items', lazy=True)
    
    def to_dict(self):
        """Convert store item to dictionary."""
        return {
            'id': self.id,
            'family_id': self.family_id,
            'name': self.name,
            'description': self.description,
            'cost': self.cost,
            'quantity': self.quantity,
            'item_type': self.item_type,
            'conversion_ratio': self.conversion_ratio,
            'created_by': self.created_by,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_by_id(cls, item_id):
        """Get store item by ID."""
        return cls.query.get(item_id)
    
    @classmethod
    def get_by_family(cls, family_id, active_only=True):
        """Get all store items for a family."""
        query = cls.query.filter_by(family_id=family_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()
    
    @classmethod
    def get_rewards_by_family(cls, family_id, active_only=True):
        """Get reward items for a family."""
        query = cls.query.filter_by(family_id=family_id, item_type='reward')
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()
    
    @classmethod
    def get_conversions_by_family(cls, family_id, active_only=True):
        """Get coins-to-points conversion items for a family."""
        query = cls.query.filter_by(family_id=family_id, item_type='coins_to_points')
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()
    
    @classmethod
    def create_item(cls, family_id, name, description, cost, created_by, 
                   quantity=None, item_type='reward', conversion_ratio=None):
        """Create a new store item."""
        item = cls(
            family_id=family_id,
            name=name,
            description=description,
            cost=cost,
            quantity=quantity,
            item_type=item_type,
            conversion_ratio=conversion_ratio,
            created_by=created_by
        )
        db.session.add(item)
        db.session.commit()
        return item
    
    def is_available(self):
        """Check if item is available for purchase."""
        return self.is_active and (self.quantity is None or self.quantity > 0)
    
    def purchase(self):
        """Handle item purchase - decrease quantity if not infinite."""
        if self.quantity is not None:
            if self.quantity <= 0:
                return False
            self.quantity -= 1
            db.session.commit()
        return True
    
    def deactivate(self):
        """Deactivate this item."""
        self.is_active = False
        db.session.commit()
    
    def update_item(self, **kwargs):
        """Update item fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()