"""
Revision model defines revisions of reviews. Each review must have at least one revision.
New revisions are created after edits. Each review contains a timestamp that indicates
a time when specific revision has been created, so you can get the latest version using
that timestamp.
"""
from critiquebrainz.data import db
from sqlalchemy.dialects.postgresql import UUID
from critiquebrainz.data.model.mixins import DeleteMixin
from datetime import datetime


class Revision(db.Model, DeleteMixin):
    __tablename__ = 'revision'

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(UUID, db.ForeignKey('review.id', ondelete='CASCADE'), index=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    text = db.Column(db.Unicode, nullable=False)

    _votes = db.relationship('Vote', cascade='delete', lazy='dynamic', backref='revision')
    _spam_reports = db.relationship('SpamReport', cascade='delete', lazy='dynamic', backref='review')

    @property
    def votes_positive_count(self):
        if hasattr(self, '_votes_positive_count') is False:
            self._votes_positive_count = self._votes.filter_by(vote=True).count()
        return self._votes_positive_count

    @property
    def votes_negative_count(self):
        if hasattr(self, '_votes_negative_count') is False:
            self._votes_negative_count = self._votes.filter_by(vote=False).count()
        return self._votes_negative_count

    def to_dict(self):
        response = dict(id=self.id,
                        review_id=self.review_id,
                        timestamp=self.timestamp,
                        text=self.text)
        return response

    @classmethod
    def create(cls, review_id, text):
        revision = cls(review_id=review_id, text=text)
        db.session.add(revision)
        db.session.commit()
        return revision
