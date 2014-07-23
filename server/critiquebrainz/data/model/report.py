from .. import db
from sqlalchemy.dialects.postgresql import UUID
from critiquebrainz.exceptions import InvalidRequest
from datetime import datetime


class SpamReport(db.Model):
    __tablename__ = 'spam_report'

    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    revision_id = db.Column(db.Integer, db.ForeignKey('revision.id', ondelete='CASCADE'), primary_key=True)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        response = dict(user_id=self.user_id,
                        review_id=self.review_id,
                        reported_at=self.reported_at)
        return response

    @classmethod
    def create(cls, review, user):
        if review.is_archived is True:
            raise InvalidRequest('archived')
        last_revision = review.revisions[-1]
        count = cls.query.filter_by(user_id=user.id, revision_id=last_revision.id).count()
        if count > 0:
            raise InvalidRequest('reported')
        report = cls(user_id=user.id, revision_id=last_revision.id)
        db.session.add(report)
        db.session.commit()
        return report

    @classmethod
    def get(cls, user, review):
        vote = cls.query.filter_by(user=user, review=review).first()
        return vote

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
