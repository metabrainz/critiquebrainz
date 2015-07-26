"""
ModerationLog model defines logs for various activities that the moderators can take
via the moderator interface. A new log entry is created for every action.
"""
from critiquebrainz.data import db
from sqlalchemy import desc
from sqlalchemy.dialects.postgresql import UUID
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.mixins import DeleteMixin
from datetime import datetime

ACTION_ARCHIVE_REVIEW = 'archive_review'
ACTION_BLOCK_USER = 'block_user'


class ModerationLog(db.Model, DeleteMixin):
    __tablename__ = 'moderation_log'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'))
    review_id = db.Column(UUID, db.ForeignKey('review.id', ondelete='CASCADE'))
    action = db.Column(db.Enum(
        ACTION_ARCHIVE_REVIEW,
        ACTION_BLOCK_USER,
        name='action_types'
    ), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reason = db.Column(db.Unicode, nullable=False)

    @property
    def user(self):
        return User.get(id=self.user_id)

    @property
    def admin(self):
        return User.get(id=self.admin_id)

    @classmethod
    def get(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def create(cls, admin_id, action, reason, user_id=None, review_id=None):
        if user_id:
            log = cls(admin_id=str(admin_id), action=action, reason=reason, user_id=str(user_id))
        elif review_id:
            log = cls(admin_id=str(admin_id), action=action, reason=reason, review_id=str(review_id))
        db.session.add(log)
        db.session.commit()
        return log

    @classmethod
    def list(cls, **kwargs):
        """Get a list of log entries.

        Args:
            admin_id: UUID of the admin whose actions generated the log.
            limit: Maximum number of reviews returned by this method.
            offset: Offset that can be used in conjunction with the limit.

        Returns:
            Pair of values: list of log entries that match applied filters and
            total number of log entries.
        """

        query = ModerationLog.query

        admin_id = kwargs.pop('admin_id', None)
        if admin_id is not None:
            query = query.filter(ModerationLog.admin_id == admin_id)

        count = query.count()

        query = query.order_by(desc(ModerationLog.timestamp))

        limit = kwargs.pop('limit', None)
        if limit is not None:
            query = query.limit(limit)

        offset = kwargs.pop('offset', None)
        if offset is not None:
            query = query.offset(offset)

        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)

        return query.all(), count
