from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class Vote(db.Model):

    __tablename__ = 'vote'
    user_id = db.Column(UUID, db.ForeignKey('user.id'), primary_key=True)
    review_id = db.Column(UUID, db.ForeignKey('review.id'), primary_key=True)
    placet = db.Column(db.Boolean, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user, review, type):
        self.user = user
        self.review = review
        self.type = type
