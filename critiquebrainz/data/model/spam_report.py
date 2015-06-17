"""
SpamReport model defines spam reports for specific revisions of reviews. Only one
spam report can be created by a single user for a specific revision.
"""
from critiquebrainz.data import db
from sqlalchemy.dialects.postgresql import UUID
from critiquebrainz.data.model.mixins import DeleteMixin
from datetime import datetime


class SpamReport(db.Model, DeleteMixin):
    __tablename__ = 'spam_report'

    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    reason = db.Column(db.Unicode)
    revision_id = db.Column(db.Integer, db.ForeignKey('revision.id', ondelete='CASCADE'), primary_key=True)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @classmethod
    def create(cls, revision_id, user, reason):
        report = cls(user=user, revision_id=revision_id, reason=reason)
        db.session.add(report)
        db.session.commit()
        return report
