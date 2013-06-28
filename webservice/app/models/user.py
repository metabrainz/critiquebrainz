from . import db
from sqlalchemy.dialects.postgresql import UUID

class User(db.Model):

    __tablename__ = 'user'
    
    id = db.Column(UUID, primary_key=True, 
        server_default=db.text("uuid_generate_v4()"))
        
    reviews = db.relationship('Review', backref=db.backref('user'))
    votes = db.relationship('Vote', backref=db.backref('user'))
    spam_reports = db.relationship('SpamReport', backref=db.backref('user'))
