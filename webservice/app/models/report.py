from app import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class SpamReport(db.Model):

    __tablename__ = 'spam_report'
    user_id = db.Column(UUID, db.ForeignKey('user.id'), primary_key=True)
    review_id = db.Column(UUID, db.ForeignKey('review.id'), primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user, review):
        self.user = user
        self.review = review
