from . import db
from sqlalchemy.dialects.postgresql import UUID
from vote import Vote
from datetime import datetime

class Review(db.Model):

    __tablename__ = 'review'
    
    id = db.Column(UUID, server_default=db.text('uuid_generate_v4()'), primary_key=True)
    release_group = db.Column(UUID, index=True)
    user_id = db.Column(UUID, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    edits = db.Column(db.Integer, nullable=False, default=0)
    rating = db.Column(db.Integer, nullable=False, default=0)
    
    votes = db.relationship('Vote', backref=db.backref('review'))
    spam_reports = db.relationship('SpamReport', backref=db.backref('review'))
    votes_up = db.relationship('Vote', 
        primaryjoin='and_(Vote.review_id == Review.id, Vote.placet == True)',
        foreign_keys=[Vote.review_id, Vote.placet])
    votes_down = db.relationship('Vote', 
        primaryjoin='and_(Vote.review_id == Review.id, Vote.placet == False)',
        foreign_keys=[Vote.review_id, Vote.placet])
        
    def to_dict(self):
        return dict(id = self.id, 
                release_group = self.release_group,
                user_id = self.user_id, 
                text = self.text, 
                created = str(self.created),
                last_updated = str(self.last_updated), 
                edits = self.edits, 
                rating = self.rating, 
                votes_overall = len(self.votes),
                votes_up = len(self.votes_up))
