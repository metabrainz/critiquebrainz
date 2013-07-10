from . import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class OAuthConsumer(db.Model):

    __tablename__ = 'oauth_consumer'
    id = db.Column(UUID, server_default=db.text('uuid_generate_v4()'),
                   primary_key=True)
    consumer_key = db.Column(UUID, server_default=db.text('uuid_generate_v4()'), 
                             index=True)
    consumer_secret = db.Column(UUID, 
                                server_default=db.text('uuid_generate_v4()'))
    user_id = db.Column(UUID, db.ForeignKey('user.id'))
    name = db.Column(db.String(128))
    desc = db.Column(db.String)
    website = db.Column(db.String(128))
    callback = db.Column(db.String)
    
    user = db.relationship('User')
    
    def __init__(self, user=None, name=None, desc=None, website=None, 
                 callback=None, consumer_key=None, consumer_secret=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.user = user
        self.name = name
        self.desc = desc
        self.website = website
        self.callback = callback
        
class OAuthAuthorizationCode(db.Model):

    __tablename__ = 'oauth_authorization_code'
    
    code = db.Column(UUID, server_default=db.text('uuid_generate_v4()'), 
                     primary_key=True)
    consumer_id = db.Column(UUID, db.ForeignKey('oauth_consumer.id'))
    user_id = db.Column(UUID, db.ForeignKey('user.id'))
    state = db.Column(db.String(128))
    scope = db.Column(db.String(128))
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    consumer = db.relationship('OAuthConsumer')
    user = db.relationship('User')
    
    def __init__(self, consumer=None, user=None, state=None, scope=None):
        self.consumer = consumer
        self.user = user
        self.state = state
        self.scope = scope
        
class OAuthAccessToken(db.Model):

    __tablename__ = 'oauth_access_token'
    
    token = db.Column(UUID, server_default=db.text('uuid_generate_v4()'), 
                      primary_key=True)
    consumer_id = db.Column(UUID, db.ForeignKey('oauth_consumer.id'))
    user_id = db.Column(UUID, db.ForeignKey('user.id'))
    scope = db.Column(db.String(128))
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expire = db.Column(db.DateTime)
    
    consumer = db.relationship('OAuthConsumer')
    user = db.relationship('User')
    
    def __init__(self, consumer=None, user=None, scope=None, expire=None):
        self.consumer = consumer
        self.user = user
        self.scope = scope
        self.expire = expire
        
class OAuthRefreshToken(db.Model):

    __tablename__ = 'oauth_refresh_token'
    
    token = db.Column(UUID, server_default=db.text('uuid_generate_v4()'), 
                      primary_key=True)
    consumer_id = db.Column(UUID, db.ForeignKey('oauth_consumer.id'))
    user_id = db.Column(UUID, db.ForeignKey('user.id'))
    scope = db.Column(db.String(128))
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    consumer = db.relationship('OAuthConsumer')
    user = db.relationship('User')
    
    def __init__(self, consumer=None, user=None, scope=None):
        self.consumer = consumer
        self.user = user
        self.scope = scope
