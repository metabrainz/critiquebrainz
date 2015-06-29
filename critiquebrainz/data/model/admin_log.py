"""
AdminLog model defines logs for various activities that the moderators can take
via the moderator interface. A new log entry is created for every action.
"""
from critiquebrainz.data import db
from sqlalchemy.dialects.postgresql import UUID
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.mixins import DeleteMixin
from datetime import datetime


class AdminLog(db.Model, DeleteMixin):
    __tablename__ = 'admin_log'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'))
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'))
    action = db.Column(db.Unicode)
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
