from datetime import datetime, date, timedelta

from sqlalchemy.dialects.postgresql import UUID

from . import db
from review import Review
from revision import Revision
from vote import Vote
from critiquebrainz.constants import user_types
import hashlib


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(UUID, primary_key=True, server_default=db.text("uuid_generate_v4()"))
    display_name = db.Column(db.Unicode, nullable=False)
    email = db.Column(db.Unicode)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    musicbrainz_id = db.Column(db.Unicode, unique=True)
    show_gravatar = db.Column(db.Boolean, nullable=False, default=True)

    _reviews = db.relationship('Review', cascade='delete', lazy='dynamic', backref='user')
    _votes = db.relationship('Vote', cascade='delete', lazy='dynamic', backref='user')
    spam_reports = db.relationship('SpamReport', cascade='delete', backref='user')
    clients = db.relationship('OAuthClient', cascade='delete', backref='user')
    grants = db.relationship('OAuthGrant', cascade='delete', backref='user')
    tokens = db.relationship('OAuthToken', cascade='delete', backref='user')

    # a list of allowed values of `inc` parameter in API calls
    allowed_includes = ('user_type', 'stats')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @classmethod
    def get_or_create(cls, display_name, **kwargs):
        # TODO: New user is created if only display_name is passed (review this behavior)
        # Display names don't have to be unique (see schema)!
        user = cls.query.filter_by(**kwargs).first()
        if user is None:
            user = cls(display_name=display_name, **kwargs)
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

    def has_voted(self, review):
        if self._votes.filter_by(review=review).count() > 0:
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
        if hasattr(self, '_karma') is False:
            # karma = sum of user's reviews ratings
            r_q = db.session.query(Vote.review_id, Vote.placet, db.func.count('*').\
                label('c')).group_by(Vote.review_id, Vote.placet)
            r_pos = r_q.subquery('r_pos')
            r_neg = r_q.subquery('r_neg')
            subquery = db.session.query(
                Review.id,
                (db.func.coalesce(r_pos.c.c, 0) -
                 db.func.coalesce(r_neg.c.c, 0)).label('rating'))
            # left join negative votes
            subquery = subquery.outerjoin(
                r_neg,
                db.and_(
                    r_neg.c.review_id==Review.id,
                    r_neg.c.placet==False))
            # left join positive votes
            subquery = subquery.outerjoin(
                r_pos,
                db.and_(
                    r_pos.c.review_id==Review.id,
                    r_pos.c.placet==True))
            subquery = subquery.filter(Review.user_id==self.id)
            # group and create a subquery
            subquery = subquery.group_by(Review.id, r_neg.c.c, r_pos.c.c)
            subquery = subquery.subquery('subquery')
            query = db.session.query(db.func.coalesce(db.func.sum(subquery.c.rating), 0))
            self._karma = int(query.scalar())
        return self._karma

    @property
    def reviews(self):
        return self._reviews.all()

    def _reviews_since(self, date):
        rev_q = db.session.query(Revision.review_id, db.func.min(Revision.timestamp).label('creation_time')) \
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

    def to_dict(self, includes=[], confidential=False, include_gravatar=True):
        response = dict(id = self.id,
            display_name = self.display_name,
            created = self.created,
            karma = self.karma,
            user_type = self.user_type.label)
        if include_gravatar is True:
            if self.show_gravatar and self.email:
                gravatar = "https://gravatar.com/avatar/" + hashlib.md5(self.email).hexdigest() + "?d=mm&r=pg"
            else:
                gravatar = "https://gravatar.com/avatar/placeholder?d=mm"
            response.update(dict(gravatar=gravatar))
        if confidential is True:
            response.update(dict(email=self.email,
                                 show_gravatar=self.show_gravatar,
                                 musicbrainz_id=self.musicbrainz_id))
        if 'user_type' in includes:
            response['user_type'] = dict(
                label = self.user_type.label,
                reviews_per_day = self.user_type.reviews_per_day,
                votes_per_day = self.user_type.votes_per_day)
        if 'stats' in includes:
            today = date.today()
            response['stats'] = dict(
                reviews_today = self.reviews_today_count(),
                reviews_last_7_days = self.reviews_since_count(
                    today-timedelta(days=7)),
                reviews_this_month = self.reviews_since_count(
                    date(today.year, today.month, 1)),
                votes_today = self.votes_today_count(),
                votes_last_7_days = self.votes_since_count(
                    today-timedelta(days=7)),
                votes_this_month = self.votes_since_count(
                    date(today.year, today.month, 1)))
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

