from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date, timedelta
from publication import Publication
from rate import Rate
from critiquebrainz.constants import user_types

class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(UUID, primary_key=True,
        server_default=db.text("uuid_generate_v4()"))
    display_name = db.Column(db.Unicode, nullable=False)
    email = db.Column(db.Unicode)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    twitter_id = db.Column(db.Unicode, unique=True)
    musicbrainz_id = db.Column(db.Unicode, unique=True)

    _publications = db.relationship('Publication', cascade='delete', lazy='dynamic', backref='user')
    _rates = db.relationship('Rate', cascade='delete', lazy='dynamic', backref='user')
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
        user = cls.query.filter_by(**kwargs).first()
        if user is None:
            user = cls(display_name=display_name,
                **kwargs)
            db.session.add(user)
            db.session.commit()
        return user

    def has_rated(self, publication):
        if self._rates.filter_by(publication=publication).count() > 0:
            return True
        else:
            return False

    @property
    def is_publication_limit_exceeded(self):
        if self.publications_today_count() >= self.user_type.publications_per_day:
            return True
        else:
            return False

    @property
    def is_rate_limit_exceeded(self):
        if self.rates_today_count() >= self.user_type.rates_per_day:
            return True
        else:
            return False

    @property
    def karma(self):
        if hasattr(self, '_karma') is False:
            # karma = sum of user's publications ratings
            r_q = db.session.query(Rate.publication_id, Rate.placet, db.func.count('*').\
                label('c')).group_by(Rate.publication_id, Rate.placet)
            r_pos = r_q.subquery('r_pos')
            r_neg = r_q.subquery('r_neg')
            subquery = db.session.query(
                Publication.id,
                (db.func.coalesce(r_pos.c.c, 0) -
                 db.func.coalesce(r_neg.c.c, 0)).label('rating'))
            # left join negative rates
            subquery = subquery.outerjoin(
                r_neg,
                db.and_(
                    r_neg.c.publication_id==Publication.id,
                    r_neg.c.placet==False))
            # left join positive rates
            subquery = subquery.outerjoin(
                r_pos,
                db.and_(
                    r_pos.c.publication_id==Publication.id,
                    r_pos.c.placet==True))
            subquery = subquery.filter(Publication.user_id==self.id)
            # group and create a subquery
            subquery = subquery.group_by(Publication.id, r_neg.c.c, r_pos.c.c)
            subquery = subquery.subquery('subquery')
            query = db.session.query(db.func.coalesce(db.func.sum(subquery.c.rating), 0))
            self._karma = int(query.scalar())
        return self._karma

    @property
    def publications(self):
        return self._publications.all()

    def _publications_since(self, date):
        return self._publications.filter(Publication.created >= date)

    def publications_since(self, date):
        return self._publications_since(date).all()

    def publications_since_count(self, date):
        return self._publications_since(date).count()

    def publications_today(self):
        return self.publications_since(date.today())

    def publications_today_count(self):
        return self.publications_since_count(date.today())

    @property
    def rates(self):
        return self._rates.all()

    def _rates_since(self, date):
        return self._rates.filter(Rate.rated_at >= date)

    def rates_since(self, date):
        return self._rates_since(date).all()

    def rates_since_count(self, date):
        return self._rates_since(date).count()

    def rates_today(self):
        return self.rates_since(date.today())

    def rates_today_count(self):
        return self.rates_since_count(date.today())

    def to_dict(self, includes=[], confidental=False):
        response = dict(id = self.id,
            display_name = self.display_name,
            created = self.created,
            karma = self.karma,
            user_type = self.user_type.label)
        if confidental is True:
            response.update(dict(email=self.email,
                                 twitter_id=self.twitter_id,
                                 musicbrainz_id=self.musicbrainz_id))
        if 'user_type' in includes:
            response['user_type'] = dict(
                label = self.user_type.label,
                publications_per_day = self.user_type.publications_per_day,
                rates_per_day = self.user_type.rates_per_day)
        if 'stats' in includes:
            today = date.today()
            response['stats'] = dict(
                publications_today = self.publications_today_count(),
                publications_last_7_days = self.publications_since_count(
                    today-timedelta(days=7)),
                publications_this_month = self.publications_since_count(
                    date(today.year, today.month, 1)),
                rates_today = self.rates_today_count(),
                rates_last_7_days = self.rates_since_count(
                    today-timedelta(days=7)),
                rates_this_month = self.rates_since_count(
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

    def update(self, display_name=None, email=None):
        if display_name is not None:
            self.display_name = display_name
        if email is not None:
            self.email = email
        db.session.commit()

