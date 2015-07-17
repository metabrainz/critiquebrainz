"""
SpamReport model defines spam reports for specific revisions of reviews. Only one
spam report can be created by a single user for a specific revision.
"""
from critiquebrainz.data import db
from sqlalchemy import desc
from sqlalchemy.dialects.postgresql import UUID
from critiquebrainz.data.model.mixins import DeleteMixin
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.revision import Revision
from datetime import datetime


class SpamReport(db.Model, DeleteMixin):
    __tablename__ = 'spam_report'

    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    reason = db.Column(db.Unicode)
    revision_id = db.Column(db.Integer, db.ForeignKey('revision.id', ondelete='CASCADE'), primary_key=True)
    reported_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_archive = db.Column(db.Boolean, nullable=False, default=False)

    @classmethod
    def get(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    @property
    def review(self):
        return Review.get(id=self.revision.review_id)

    @classmethod
    def create(cls, revision_id, user, reason):
        report = cls(user=user, revision_id=revision_id, reason=reason)
        db.session.add(report)
        db.session.commit()
        return report

    def archive(self):
        self.is_archive = True
        db.session.commit()

    @classmethod
    def list(cls, **kwargs):
        """Get a list of reports.

        Args:
            review_id: UUID of the review that is associated with the report.
            user_id: UUID of the user who created the report.
            limit: Maximum number of reviews returned by this method.
            offset: Offset that can be used in conjunction with the limit.

        Returns:
            Pair of values: list of report that match applied filters and
            total number of reports.
        """

        query = SpamReport.query

        review_id = kwargs.pop('review_id', None)
        if review_id is not None:
            revision_ids = db.session.query(Revision.id).filter_by(review_id=review_id)
            query = SpamReport.query.filter(SpamReport.revision_id.in_(revision_ids))

        user_id = kwargs.pop('user_id', None)
        if user_id is not None:
            query = query.filter(SpamReport.user_id == user_id)

        count = query.count()

        query = query.order_by(desc(SpamReport.reported_at))

        limit = kwargs.pop('limit', None)
        if limit is not None:
            query = query.limit(limit)

        offset = kwargs.pop('offset', None)
        if offset is not None:
            query = query.offset(offset)

        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)

        return query.all(), count
