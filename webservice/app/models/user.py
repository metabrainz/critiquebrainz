from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class User(db.Model):

    __tablename__ = 'user'
    
    id = db.Column(UUID, primary_key=True, 
                   server_default=db.text("uuid_generate_v4()"))
    display_name = db.Column(db.String(128))
    email = db.Column(db.String(128))
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        
    publications = db.relationship('Publication')
    rates = db.relationship('Rate', backref=db.backref('user'))
    spam_reports = db.relationship('SpamReport', backref=db.backref('user'))
    oauth_consumers = db.relationship('OAuthConsumer')
    
    def __init__(self, display_name=None, email=None):
        self.display_name = display_name
        self.email = email
        
    def to_dict(self, includes=None):
        response = dict(id = self.id)
        return response
