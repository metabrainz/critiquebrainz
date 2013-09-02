from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date
from publication import Publication
from critiquebrainz.constants import user_types

class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(UUID, primary_key=True,
        server_default=db.text("uuid_generate_v4()"))
    display_name = db.Column(db.Unicode, nullable=False)
    email = db.Column(db.Unicode)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    karma = db.Column(db.Integer, nullable=False, default=0)
    twitter_id = db.Column(db.Unicode, unique=True)
    musicbrainz_id = db.Column(db.Unicode, unique=True)

    _publications = db.relationship('Publication', cascade='delete', lazy='dynamic', backref='user')
    _rates = db.relationship('Rate', cascade='delete', backref='user')
    spam_reports = db.relationship('SpamReport', cascade='delete', backref='user')
    clients = db.relationship('OAuthClient', cascade='delete', backref='user')
    grants = db.relationship('OAuthGrant', cascade='delete', backref='user')
    tokens = db.relationship('OAuthToken', cascade='delete', backref='user')

    # a list of allowed values of `inc` parameter in API calls
    allowed_includes = ('publications', )

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

    @property
    def is_publication_limit_exceeded(self):
        if self.publications_today_count() >= self.user_type.get('publications_per_day'):
            return True
        else:
            return False

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

    def to_dict(self, includes=[], confidental=False):
        response = dict(id = self.id,
            display_name = self.display_name,
            created = self.created,
            karma = self.karma,
            user_type = self.user_type, )
        if confidental is True:
            response.update(dict(email=self.email,
                                 twitter_id=self.twitter_id,
                                 musicbrainz_id=self.musicbrainz_id))
        if 'publications' in includes:
            response['publications'] = [p.to_dict() for p in self.publications]
        return response

    @property
    def user_type(self):
        def get_user_type(karma):
            for user_type in user_types:
                if user_type is None or karma > user_type.get('karma'):
                    return user_type
        if hasattr(self, '_user_type') is False:
            self._user_type = get_user_type(self.karma)
        return self._user_type

    def update(self, display_name=None, email=None):
        if display_name is not None:
            self.display_name = display_name
        if email is not None:
            self.email = email
        db.session.commit()
