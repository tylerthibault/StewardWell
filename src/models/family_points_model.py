"""
Family Points Model

Handles database operations for family points pool and transactions.
"""

from datetime import datetime
from src import db


class FamilyPoints(db.Model):
    """Family points model for shared points pool."""
    
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False, unique=True)
    total_points = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    family = db.relationship('Family', backref='family_points', lazy=True)
    updater = db.relationship('User', backref='updated_family_points', lazy=True)
    
    def to_dict(self):
        """Convert family points to dictionary."""
        return {
            'id': self.id,
            'family_id': self.family_id,
            'total_points': self.total_points,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'updated_by': self.updated_by
        }
    
    @classmethod
    def get_by_family(cls, family_id):
        """Get family points by family ID, create if doesn't exist."""
        points = cls.query.filter_by(family_id=family_id).first()
        if not points:
            points = cls.create_family_points(family_id)
        return points
    
    @classmethod
    def create_family_points(cls, family_id):
        """Create family points record."""
        points = cls(family_id=family_id, total_points=0)
        db.session.add(points)
        db.session.commit()
        return points
    
    def add_points(self, amount, updated_by=None):
        """Add points to family pool."""
        self.total_points += amount
        self.last_updated = datetime.utcnow()
        self.updated_by = updated_by
        db.session.commit()
        return self.total_points
    
    def subtract_points(self, amount, updated_by=None):
        """Subtract points from family pool."""
        if self.total_points >= amount:
            self.total_points -= amount
            self.last_updated = datetime.utcnow()
            self.updated_by = updated_by
            db.session.commit()
            return self.total_points
        return None  # Insufficient points
    
    def set_points(self, amount, updated_by=None):
        """Set total points to specific amount."""
        self.total_points = amount
        self.last_updated = datetime.utcnow()
        self.updated_by = updated_by
        db.session.commit()
        return self.total_points


class PointsTransaction(db.Model):
    """Points transaction model for tracking point changes."""
    
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Who initiated the transaction
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=True)  # If transaction involves a child
    amount = db.Column(db.Integer, nullable=False)  # Positive for earned, negative for spent
    transaction_type = db.Column(db.String(30), nullable=False)  # chore_completion, manual_adjustment, store_purchase, coins_conversion
    description = db.Column(db.String(200))
    reference_id = db.Column(db.Integer, nullable=True)  # ID of chore, store item, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    family = db.relationship('Family', backref='points_transactions', lazy=True)
    user = db.relationship('User', backref='points_transactions', lazy=True)
    child = db.relationship('Child', backref='points_transactions', lazy=True)
    
    def to_dict(self):
        """Convert transaction to dictionary."""
        return {
            'id': self.id,
            'family_id': self.family_id,
            'user_id': self.user_id,
            'child_id': self.child_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'reference_id': self.reference_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_transaction(cls, family_id, amount, transaction_type, description, 
                          user_id=None, child_id=None, reference_id=None):
        """Create a new points transaction."""
        transaction = cls(
            family_id=family_id,
            user_id=user_id,
            child_id=child_id,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            reference_id=reference_id
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    @classmethod
    def get_by_family(cls, family_id, limit=50):
        """Get recent transactions for a family."""
        return cls.query.filter_by(family_id=family_id)\
                      .order_by(cls.created_at.desc())\
                      .limit(limit).all()
    
    @classmethod
    def get_by_type(cls, family_id, transaction_type, limit=50):
        """Get transactions of a specific type for a family."""
        return cls.query.filter_by(family_id=family_id, transaction_type=transaction_type)\
                      .order_by(cls.created_at.desc())\
                      .limit(limit).all()
    
    def get_actor_name(self):
        """Get the name of who initiated this transaction."""
        if self.user_id:
            from src.models.user_model import User
            user = User.get_by_id(self.user_id)
            return user.username if user else 'Unknown Adult'
        elif self.child_id:
            from src.models.child_model import Child
            child = Child.get_by_id(self.child_id)
            return child.name if child else 'Unknown Child'
        return 'System'