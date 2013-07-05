from . import db
from sqlalchemy.dialects.postgresql import UUID
from rate import Rate
from datetime import datetime

class Publication(db.Model):

    __tablename__ = 'publication'
    
    id = db.Column(UUID, server_default=db.text('uuid_generate_v4()'), primary_key=True)
    release_group = db.Column(UUID, index=True)
    user_id = db.Column(UUID, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    edits = db.Column(db.Integer, nullable=False, default=0)
    rating = db.Column(db.Integer, nullable=False, default=0)
    
    user = db.relationship('User')
    rates = db.relationship('Rate', backref=db.backref('publication'))
    spam_reports = db.relationship('SpamReport', backref=db.backref('publication'))
    rates_positive = db.relationship('Rate', 
        primaryjoin='and_(Rate.publication_id == Publication.id, Rate.placet == True)',
        foreign_keys=[Rate.publication_id, Rate.placet])
    rates_negative = db.relationship('Rate', 
        primaryjoin='and_(Rate.publication_id == Publication.id, Rate.placet == False)',
        foreign_keys=[Rate.publication_id, Rate.placet])
        
    VALID_INCLUDES = ['user']

    def __init__(self, user=None, text=None, release_group=None):
        self.user = user
        self.text = text
        self.release_group = release_group

    def to_dict(self, includes=None):
        response = dict(id = self.id, 
                        release_group = self.release_group,
                        user_id = self.user_id, 
                        text = self.text, 
                        created = str(self.created),
                        last_updated = str(self.last_updated), 
                        edits = self.edits, 
                        rating = self.rating, 
                        rates = len(self.rates),
                        rates_positive = len(self.rates_positive),
                        rates_negative = len(self.rates_negative))
        if includes and 'user' in includes:
            response['user'] = self.user.to_dict()
        return response
