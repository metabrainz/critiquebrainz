from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class Rate(db.Model):

    __tablename__ = 'rate'
    user_id = db.Column(UUID, db.ForeignKey('user.id'), primary_key=True)
    publication_id = db.Column(UUID, db.ForeignKey('publication.id'), primary_key=True)
    placet = db.Column(db.Boolean, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user, review, placet):
        self.user = user
        self.publication = publication
        self.placet = placet
