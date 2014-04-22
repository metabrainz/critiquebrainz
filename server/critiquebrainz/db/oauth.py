from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from critiquebrainz.utils import generate_string

class OAuthClient(db.Model):

    __tablename__ = 'oauth_client'

    client_id = db.Column(db.Unicode, primary_key=True)
    client_secret = db.Column(db.Unicode, nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'))
    name = db.Column(db.Unicode, nullable=False)
    desc = db.Column(db.Unicode, nullable=False)
    website = db.Column(db.Unicode, nullable=False)
    redirect_uri = db.Column(db.UnicodeText, nullable=False)
    scopes = db.Column(db.UnicodeText, default=u'user review')

    grants = db.relationship('OAuthGrant', cascade='all', backref='client')
    tokens = db.relationship('OAuthToken', cascade='all', backref='client')

    allowed_includes = []

    @classmethod
    def generate(cls, user, name, desc, website, redirect_uri, scopes):
        client_id = generate_string(20)
        client_secret = generate_string(40)
        client = cls(client_id=client_id, client_secret=client_secret, user=user,
            name=name, desc=desc, website=website, redirect_uri=redirect_uri, scopes=' '.join(scopes))
        db.session.add(client)
        db.session.commit()
        return client

    def get_scopes(self):
        if hasattr(self, '_scopes') is False:
            self._scopes = self.scopes.split()
        return self._scopes

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    def to_dict(self, includes=[]):
        response = dict(client_id=self.client_id,
            client_secret=self.client_secret,
            user_id=self.user_id,
            name=self.name,
            desc=self.desc,
            website=self.website,
            redirect_uri=self.redirect_uri,
            scopes=self.scopes)
        return response

    def update(self, name=None, desc=None, website=None, redirect_uri=None, scopes=None):
        if name is not None:
            self.name = name
        if desc is not None:
            self.desc = desc
        if website is not None:
            self.website = website
        if redirect_uri is not None:
            self.redirect_uri = redirect_uri
        if scopes is not None:
            self.scopes = ' '.join(scopes)
        db.session.commit()


class OAuthGrant(db.Model):

    __tablename__ = 'oauth_grant'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode, index=True, nullable=False)
    client_id = db.Column(db.Unicode, db.ForeignKey('oauth_client.client_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
    redirect_uri = db.Column(db.UnicodeText, nullable=False)
    scopes = db.Column(db.UnicodeText)

    def get_scopes(self):
        if hasattr(self, '_scopes') is False:
            self._scopes = self.scopes.split()
        return self._scopes

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

class OAuthToken(db.Model):

    __tablename__ = 'oauth_token'

    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.Unicode, unique=True, nullable=False)
    refresh_token = db.Column(db.Unicode, unique=True, nullable=False)
    client_id = db.Column(db.Unicode, db.ForeignKey('oauth_client.client_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
    scopes = db.Column(db.UnicodeText)

    def get_scopes(self):
        if hasattr(self, '_scopes') is False:
            self._scopes = self.scopes.split()
        return self._scopes

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @classmethod
    def purge_tokens(cls, client_id, user_id):
        cls.query.filter_by(client_id=client_id, user_id=user_id).delete()
        db.session.commit()

    def to_dict(self, includes=[]):
        response = dict(refresh_token=self.refresh_token,
            scopes=self.scopes,
            client=self.client.to_dict())
        return response


