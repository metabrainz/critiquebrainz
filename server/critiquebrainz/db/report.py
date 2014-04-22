from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class SpamReport(db.Model):

    __tablename__ = 'spam_report'
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    review_id = db.Column(UUID, db.ForeignKey('review.id', ondelete='CASCADE'), primary_key=True)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, user, review):
        self.user = user
        self.review = review

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
