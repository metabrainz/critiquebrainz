from app import db
from sqlalchemy.dialects.postgresql import UUID

class Vote(db.Model):

    __tablename__ = 'vote'
    user_id = db.Column(UUID, db.ForeignKey('user.id'), primary_key=True)
    review_id = db.Column(UUID, db.ForeignKey('review.id'), primary_key=True)
    type = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, nullable=False, server_default=db.text("now()"))
    
    def __init__(self, user, review, type):
        self.user = user
        self.review = review
        self.type = type
