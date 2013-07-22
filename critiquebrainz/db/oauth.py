from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class OAuthClient(db.Model):

    __tablename__ = 'oauth_client'
    client_id = db.Column(db.Unicode, primary_key=True)
    client_secret = db.Column(db.Unicode, nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id'))
    name = db.Column(db.Unicode, nullable=False)
    desc = db.Column(db.Unicode, nullable=False)
    website = db.Column(db.Unicode, nullable=False)
    _redirect_uris = db.Column(db.UnicodeText, nullable=False)
    _default_scopes = db.Column(db.UnicodeText, default=u'user publication')
    is_confidential = db.Column(db.Boolean, nullable=False, default=True)

    user = db.relationship('User')

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

    def validate_redirect_uri(self, redirect_uri):
        redirect_uri = redirect_uri.split('?')[0]
        return redirect_uri in self.redirect_uris

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
        
class OAuthGrant(db.Model):

    __tablename__ = 'oauth_grant'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Unicode, index=True, nullable=False)
    client_id = db.Column(db.Unicode, db.ForeignKey('oauth_client.client_id', 
        onupdate='CASCADE'), nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id'), nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
    redirect_uri = db.Column(db.UnicodeText, nullable=False)
    _scopes = db.Column(db.UnicodeText)

    client = db.relationship('OAuthClient')
    user = db.relationship('User')

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
        
class OAuthToken(db.Model):

    __tablename__ = 'oauth_token'
    
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.Unicode, unique=True, nullable=False)
    refresh_token = db.Column(db.Unicode, unique=True, nullable=False)
    token_type = db.Column(db.Unicode, nullable=False)
    client_id = db.Column(db.Unicode, db.ForeignKey('oauth_client.client_id', 
        onupdate='CASCADE'), nullable=False)
    user_id = db.Column(UUID, db.ForeignKey('user.id'), nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
    _scopes = db.Column(db.UnicodeText)

    client = db.relationship('OAuthClient')
    user = db.relationship('User')

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

