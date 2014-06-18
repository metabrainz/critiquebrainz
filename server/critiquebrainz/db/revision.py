from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from . import db


class Revision(db.Model):
    __tablename__ = 'revision'

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(UUID, db.ForeignKey('review.id', ondelete='CASCADE'), index=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    text = db.Column(db.Unicode, nullable=False)

    _votes = db.relationship('Vote', cascade='delete', lazy='dynamic', backref='revision')
    _spam_reports = db.relationship('SpamReport', cascade='delete', lazy='dynamic', backref='review')

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
