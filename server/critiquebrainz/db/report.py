from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class SpamReport(db.Model):

    __tablename__ = 'spam_report'
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    publication_id = db.Column(UUID, db.ForeignKey('publication.id', ondelete='CASCADE'), primary_key=True)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, user, publication):
        self.user = user
        self.publication = publication

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
