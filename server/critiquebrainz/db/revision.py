from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from . import db


class Revision(db.Model):
    __tablename__ = 'revision'

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(UUID, db.ForeignKey('review.id', ondelete='CASCADE'), primary_key=True, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    text = db.Column(db.Unicode, nullable=False)

    def to_dict(self):
        response = dict(id=self.id,
                        review_id=self.review_id,
                        timestamp=self.timestamp,
                        text=self.text)
        return response

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
