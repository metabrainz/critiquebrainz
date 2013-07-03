from . import db
from sqlalchemy.dialects.postgresql import UUID

class User(db.Model):

    __tablename__ = 'user'
    
    id = db.Column(UUID, primary_key=True, 
        server_default=db.text("uuid_generate_v4()"))
        
    publications = db.relationship('Publication', backref=db.backref('user'))
    rates = db.relationship('Rate', backref=db.backref('user'))
    spam_reports = db.relationship('SpamReport', backref=db.backref('user'))
