from critiquebrainz.data import db
from sqlalchemy.orm import backref
from sqlalchemy.dialects.postgresql import UUID
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.revision import Revision
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.data.model.mixins import DeleteMixin, AdminMixin
from critiquebrainz.data.constants import user_types
from datetime import datetime, date, timedelta
import hashlib


class User(db.Model, AdminMixin, DeleteMixin):
    __tablename__ = 'user'

    id = db.Column(UUID, primary_key=True, server_default=db.text('uuid_generate_v4()'))
    display_name = db.Column(db.Unicode, nullable=False)
    email = db.Column(db.Unicode)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    musicbrainz_id = db.Column(db.Unicode, unique=True)
    show_gravatar = db.Column(db.Boolean, nullable=False, server_default="False")
    is_blocked = db.Column(db.Boolean, nullable=False, server_default="False")

    spam_reports = db.relationship('SpamReport', cascade='delete', backref='user')
    clients = db.relationship('OAuthClient', cascade='delete', backref='user')
    grants = db.relationship('OAuthGrant', cascade='delete', backref='user')
    tokens = db.relationship('OAuthToken', cascade='delete', backref='user')

    _reviews = db.relationship('Review', cascade='delete', lazy='dynamic', backref=backref('user', lazy='joined'))
    _votes = db.relationship('Vote', cascade='delete', lazy='dynamic', backref='user')

    # a list of allowed values of `inc` parameter in API calls
    allowed_includes = ('user_type', 'stats')

    @classmethod
    def get(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def get_or_create(cls, display_name, musicbrainz_id, **kwargs):
        user = cls.query.filter_by(musicbrainz_id=musicbrainz_id, **kwargs).first()
        if user is None:
            user = cls(display_name=display_name, musicbrainz_id=musicbrainz_id, **kwargs)
            db.session.add(user)
            db.session.commit()
        return user

    @classmethod
    def list(cls, limit=None, offset=None):
        query = User.query
        count = query.count()
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        users = query.all()
        return users, count

    @classmethod
    def get_count(cls):
        return cls.query.count()

    def has_voted(self, review):
        if self._votes.filter_by(revision=review.last_revision).count() > 0:
            return True
        else:
            return False

    @property
    def is_review_limit_exceeded(self):
        if self.reviews_today_count() >= self.user_type.reviews_per_day:
            return True
        else:
            return False

    @property
    def is_vote_limit_exceeded(self):
        if self.votes_today_count() >= self.user_type.votes_per_day:
            return True
        else:
            return False

    @property
    def karma(self):
        """User's karma. Based on ratings of revisions."""
        if hasattr(self, '_karma') is False:
            # TODO: Improve this
            q = db.session.query(Vote).outerjoin(Revision).outerjoin(Review).outerjoin(User).filter(User.id == self.id)
            query_pos = q.filter(Vote.vote == True)
            query_neg = q.filter(Vote.vote == False)
            self._karma = query_pos.count() - query_neg.count()
        return self._karma

    @property
    def reviews(self):
        return self._reviews.all()

    @property
    def avatar(self):
        """Link to user's avatar image."""
        if self.show_gravatar and self.email:
            return "https://gravatar.com/avatar/" + hashlib.md5(self.email.encode("utf-8")).hexdigest() + "?d=identicon&r=pg"
        else:
            return "https://gravatar.com/avatar/" + hashlib.md5(self.id.encode("utf-8")).hexdigest() + "?d=identicon"

    @property
    def stats(self):
        today = date.today()
        return dict(
            reviews_today=self.reviews_today_count(),
            reviews_last_7_days=self.reviews_since_count(today-timedelta(days=7)),
            reviews_this_month=self.reviews_since_count(date(today.year, today.month, 1)),
            votes_today=self.votes_today_count(),
            votes_last_7_days=self.votes_since_count(today-timedelta(days=7)),
            votes_this_month=self.votes_since_count(date(today.year, today.month, 1)))

    def _reviews_since(self, date):
        rev_q = db.session.query(Revision.review_id, db.func.min(Revision.timestamp).label('creation_time'))\
            .group_by(Revision.review_id).subquery('time')
        return self._reviews.outerjoin(rev_q, Review.id == rev_q.c.review_id).filter(rev_q.c.creation_time >= date)

    def reviews_since(self, date):
        return self._reviews_since(date).all()

    def reviews_since_count(self, date):
        return self._reviews_since(date).count()

    def reviews_today(self):
        return self.reviews_since(date.today())

    def reviews_today_count(self):
        return self.reviews_since_count(date.today())

    @property
    def votes(self):
        return self._votes.all()

    def _votes_since(self, date):
        return self._votes.filter(Vote.rated_at >= date)

    def votes_since(self, date):
        return self._votes_since(date).all()

    def votes_since_count(self, date):
        return self._votes_since(date).count()

    def votes_today(self):
        return self.votes_since(date.today())

    def votes_today_count(self):
        return self.votes_since_count(date.today())

    def to_dict(self, includes=None, confidential=False):
        if includes is None:
            includes = []
        response = dict(id=self.id,
                        display_name=self.display_name,
                        created=self.created,
                        karma=self.karma,
                        user_type=self.user_type.label)

        if confidential is True:
            response.update(dict(email=self.email,
                                 avatar=self.avatar,
                                 show_gravatar=self.show_gravatar,
                                 musicbrainz_id=self.musicbrainz_id))

        if 'user_type' in includes:
            response['user_type'] = dict(
                label=self.user_type.label,
                reviews_per_day=self.user_type.reviews_per_day,
                votes_per_day=self.user_type.votes_per_day)

        if 'stats' in includes:
            today = date.today()
            response['stats'] = dict(
                reviews_today=self.reviews_today_count(),
                reviews_last_7_days=self.reviews_since_count(today - timedelta(days=7)),
                reviews_this_month=self.reviews_since_count(date(today.year, today.month, 1)),
                votes_today=self.votes_today_count(),
                votes_last_7_days=self.votes_since_count(today - timedelta(days=7)),
                votes_this_month=self.votes_since_count(date(today.year, today.month, 1)))

        return response

    @property
    def user_type(self):
        def get_user_type(user):
            for user_type in user_types:
                if user_type.is_instance(user):
                    return user_type
        if hasattr(self, '_user_type') is False:
            self._user_type = get_user_type(self)
        return self._user_type

    def update(self, display_name=None, email=None, show_gravatar=None):
        if display_name is not None:
            self.display_name = display_name
        if show_gravatar is not None:
            self.show_gravatar = show_gravatar
        self.email = email
        db.session.commit()

    def block(self):
        self.is_blocked = True
        db.session.commit()

    def unblock(self):
        self.is_blocked = False
        db.session.commit()
