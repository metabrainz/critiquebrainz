from app import db
from app.votes.models import Vote
from utils import compute_rating

from sqlalchemy.dialects.postgresql import UUID
import datetime

class Review(db.Model):

    __tablename__ = 'review'
    
    id = db.Column(UUID, server_default=db.text('uuid_generate_v4()'), primary_key=True)
    release_group_id = db.Column(UUID, index=True)
    user_id = db.Column(UUID, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, server_default=db.text("now()"))
    last_updated = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    edits = db.Column(db.Integer, nullable=False, server_default=db.text("0"))
    rating = db.Column(db.Integer, nullable=False, server_default=db.text("0"))
    
    votes = db.relationship('Vote', backref=db.backref('review'), lazy='dynamic')
    spam_reports = db.relationship('SpamReport', backref=db.backref('review'))

    def __init__(self, user, text, release_group_id):
        self.user = user
        self.text = text
        self.release_group_id = release_group_id
        
    @property
    def votes_overall(self):
        return self.votes.count()
        
    @property
    def votes_positive(self):
        return self.votes.filter(Vote.type > 0).count()
        
    def update_rating(self):
        """ Compute and update the rank """
        self.rating = compute_rating(self.votes_overall, self.votes_positive)
        
    def to_dict(self):
        return dict(id = self.id, release_group_id = self.release_group_id,
                user_id = self.user_id, text = self.text, created = str(self.created),
                last_updated = str(self.last_updated), edits = self.edits, 
                rating = self.rating, votes_overall = self.votes_overall,
                votes_positive = self.votes_positive)
