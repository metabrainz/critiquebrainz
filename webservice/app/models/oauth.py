from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class OAuthClient(db.Model):

    __tablename__ = 'oauth_client'
    id = db.Column(db.String(64), primary_key=True)
    secret = db.Column(db.String(64))
    user_id = db.Column(UUID, db.ForeignKey('user.id'))
    name = db.Column(db.String(128))
    desc = db.Column(db.String)
    website = db.Column(db.String(128))
    redirect_uri = db.Column(db.String)
    
    user = db.relationship('User')
    
    def __init__(self, id=None, secret=None, user=None, 
                 name=None, desc=None, website=None, redirect_uri=None):
        self.id = id
        self.secret = secret
        self.user = user
        self.name = name
        self.desc = desc
        self.website = website
        self.redirect_uri = redirect_uri
        
class OAuthAuthorizationCode(db.Model):

    __tablename__ = 'oauth_authorization_code'
    
    code = db.Column(db.String(64), primary_key=True)
    client_id = db.Column(db.String(64), db.ForeignKey('oauth_client.id', onupdate='CASCADE'))
    user_id = db.Column(UUID, db.ForeignKey('user.id'))
    scope = db.Column(db.String(128))
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    client = db.relationship('OAuthClient')
    user = db.relationship('User')
    
    def __init__(self, code=None, client=None, user=None, scope=None):
        self.code = code
        self.client = client
        self.user = user
        self.scope = scope
        
class OAuthAccessToken(db.Model):

    __tablename__ = 'oauth_access_token'
    
    token = db.Column(db.String(64), primary_key=True)
    client_id = db.Column(db.String(64), db.ForeignKey('oauth_client.id', onupdate='CASCADE'))
    user_id = db.Column(UUID, db.ForeignKey('user.id'))
    scope = db.Column(db.String(64))
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expire = db.Column(db.DateTime)
    
    client = db.relationship('OAuthClient')
    user = db.relationship('User')
    
    def __init__(self, token=None, client=None, user=None, scope=None, 
                 expire=None):
        self.token = token
        self.client = client
        self.user = user
        self.scope = scope
        self.expire = expire
        
class OAuthRefreshToken(db.Model):

    __tablename__ = 'oauth_refresh_token'
    
    token = db.Column(db.String(64), primary_key=True)
    client_id = db.Column(db.String(64), db.ForeignKey('oauth_client.id', onupdate='CASCADE'))
    user_id = db.Column(UUID, db.ForeignKey('user.id'))
    scope = db.Column(db.String(64))
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    client = db.relationship('OAuthClient')
    user = db.relationship('User')
    
    def __init__(self, token=None, client=None, user=None, scope=None):
        self.token = token
        self.client = client
        self.user = user
        self.scope = scope
