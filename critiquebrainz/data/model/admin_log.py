"""
AdminLog model defines logs for various activities that the moderators can take
via the moderator interface. A new log entry is created for every action.
"""
from critiquebrainz.data import db
from sqlalchemy import desc
from sqlalchemy.dialects.postgresql import UUID
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.mixins import DeleteMixin
from datetime import datetime

ACTION_ARCHIVE_REVIEW = 'archive_review'
ACTION_BAN_USER = 'ban_user'


class AdminLog(db.Model, DeleteMixin):
    __tablename__ = 'admin_log'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'))
    action = db.Column(db.Enum(
        ACTION_ARCHIVE_REVIEW,
        ACTION_BAN_USER,
        name='action_types'
    ), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

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
    def create(cls, admin_id, user_id, action):
        log = cls(admin_id=str(admin_id), user_id=str(user_id), action=action)
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

        query = AdminLog.query

        admin_id = kwargs.pop('admin_id', None)
        if admin_id is not None:
            query = query.filter(AdminLog.admin_id == admin_id)

        count = query.count()

        query = query.order_by(desc(AdminLog.timestamp))

        limit = kwargs.pop('limit', None)
        if limit is not None:
            query = query.limit(limit)

        offset = kwargs.pop('offset', None)
        if offset is not None:
            query = query.offset(offset)

        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)

        return query.all(), count
