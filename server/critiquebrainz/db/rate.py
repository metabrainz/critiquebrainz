from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class Rate(db.Model):

    __tablename__ = 'rate'
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), 
        primary_key=True)
    publication_id = db.Column(UUID, db.ForeignKey('publication.id', 
        ondelete='CASCADE'), primary_key=True)
    placet = db.Column(db.Boolean, nullable=False)
    rated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    user = db.relationship('User')
    publication = db.relationship('Publication')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
