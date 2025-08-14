"""
Join Request Model

Represents a parent's request to join a family, pending approval by the family manager (creator).
"""
from datetime import datetime
from src import db


class JoinRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending|approved|rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='join_requests', lazy=True)
    family = db.relationship('Family', backref='join_requests', lazy=True)

    @classmethod
    def get_pending_by_family(cls, family_id):
        return cls.query.filter_by(family_id=family_id, status='pending').all()

    @classmethod
    def get_pending_for_user_family(cls, user_id, family_id):
        return cls.query.filter_by(user_id=user_id, family_id=family_id, status='pending').first()

    @classmethod
    def create_request(cls, user_id, family_id):
        existing = cls.get_pending_for_user_family(user_id, family_id)
        if existing:
            return existing
        jr = cls(user_id=user_id, family_id=family_id, status='pending')
        db.session.add(jr)
        db.session.commit()
        return jr

    def approve(self):
        from src.models.user_model import User
        if self.status != 'pending':
            return False
        self.status = 'approved'
        user = User.get_by_id(self.user_id)
        if not user:
            return False
        user.family_id = self.family_id
        db.session.commit()
        return True

    def reject(self):
        if self.status != 'pending':
            return False
        self.status = 'rejected'
        db.session.commit()
        return True
