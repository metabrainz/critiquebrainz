from flask import request
from critiquebrainz.db import db, OAuthClient, OAuthGrant, OAuthToken
from critiquebrainz.utils import generate_string
from exceptions import *
from datetime import datetime, timedelta
from functools import wraps

class CritiqueBrainzAuthorizationProvider(object):

    def init_app(self, app):
        self.token_length = app.config['OAUTH_TOKEN_LENGTH']
        self.grant_expire = app.config['OAUTH_GRANT_EXPIRE']
        self.token_expire = app.config['OAUTH_TOKEN_EXPIRE']

    def validate_authorization_header(self, value):
        if not value or isinstance(value, unicode) is False:
            return False

        authorization = value.split()
        if len(authorization) != 2:
            return False

        if authorization[0] != 'Bearer':
            return False

        return True

    def validate_client_id(self, client_id):
        if not client_id:
            return False
        return OAuthClient.query.get(client_id) is not None

    def validate_client_secret(self, client_id, client_secret):
        client = OAuthClient.query.get(client_id)
        if client is None:
            return False
        else:
            return client.client_secret == client_secret
            
    def validate_client_redirect_uri(self, client_id, redirect_uri):
        client = OAuthClient.query.get(client_id)

        if client is None or isinstance(redirect_uri, unicode) is False:
            return False
        else:
            return client.redirect_uri == redirect_uri.split('?')[0]

    def validate_client_scope(self, client_id, scope):
        client = OAuthClient.query.get(client_id)
        return self.validate_scope(scope, client.get_scopes())

    def validate_grant_redirect_uri(self, client_id, code, redirect_uri):
        grant = self.fetch_grant(client_id, code)

        if grant is None:
            return False
        else:
            return grant.redirect_uri == redirect_uri

    def validate_grant_scope(self, client_id, code, scope):
        grant = self.fetch_grant(client_id, code)
        return self.validate_scope(scope, grant.get_scopes())

    def validate_grant(self, client_id, code):
        grant = self.fetch_grant(client_id, code)
        if grant is None:
            return False
        return ( datetime.now() > grant.expires ) is False

    def validate_token_scope(self, client_id, refresh_token, scope):
        token = self.fetch_token(client_id, refresh_token)
        return self.validate_scope(scope, token.get_scopes())

    def validate_token(self, client_id, refresh_token):
        return self.fetch_token(client_id, refresh_token) is not None

    def validate_scope(self, scope, valid_scopes):
        if not scope or isinstance(scope, unicode) is False:
            return False

        scopes = scope.split()
        for scope in scopes:
            if scope not in valid_scopes:
                return False
        return True

    def persist_grant(self, client_id, code, scopes, expires, redirect_uri, user_id):
        grant = OAuthGrant(client_id=client_id,
                           code=code,
                           scopes=scopes,
                           expires=expires,
                           redirect_uri=redirect_uri,
                           user_id=user_id)

        db.session.add(grant)
        db.session.commit()
        return grant

    def persist_token(self, client_id, scopes, refresh_token, access_token, expires, user_id):
        token = OAuthToken(client_id=client_id,
                           scopes=scopes,
                           access_token=access_token,
                           refresh_token=refresh_token,
                           expires=expires,
                           user_id=user_id)

        db.session.add(token)
        db.session.commit()
        return token

    def fetch_grant(self, client_id, code):
        grant = OAuthGrant.query.filter_by(client_id=client_id, code=code).first()
        return grant

    def fetch_token(self, client_id, refresh_token):
        token = OAuthToken.query.filter_by(client_id=client_id, refresh_token=refresh_token).first()
        return token

    def fetch_access_token(self, access_token):
        token = OAuthToken.query.filter_by(access_token=access_token).first()
        return token

    def discard_grant(self, client_id, code):
        OAuthGrant.query.filter_by(client_id=client_id, code=code).delete()

    def discard_token(self, client_id, refresh_token):
        OAuthToken.query.filter_by(client_id=client_id, refresh_token=refresh_token).delete()

    def discard_client_user_tokens(self, client_id, user_id):
        OAuthToken.query.filter_by(client_id=client_id, user_id=user_id).delete()

    def validate_authorization_request(self, client_id, response_type, redirect_uri, scope):
        if self.validate_client_id(client_id) is False:
            raise InvalidClient
        if response_type != 'code':
            raise UnsupportedResponseType
        if self.validate_client_redirect_uri(client_id, redirect_uri) is False:
            raise InvalidRedirectURI
        if self.validate_client_scope(client_id, scope) is False:
            raise InvalidScope

    def validate_token_request(self, client_id, client_secret, grant_type, scope, code, refresh_token, redirect_uri):
        if self.validate_client_id(client_id) is False:
            raise InvalidClient
        if self.validate_client_secret(client_id, client_secret) is False:
            raise InvalidClient
        if grant_type == 'code':
            if self.validate_grant(client_id, code) is False:
                raise InvalidGrant
            if self.validate_grant_scope(client_id, code, scope) is False:
                raise InvalidScope
            if self.validate_grant_redirect_uri(client_id, code, redirect_uri) is False:
                raise InvalidRedirectURI
        elif grant_type == 'refresh_token':
            if self.validate_token(client_id, refresh_token) is False:
                raise InvalidGrant
            if self.validate_token_scope(client_id, refresh_token, scope) is False:
                raise InvalidScope
        else:
            raise UnsupportedGrantType

    def generate_grant(self, client_id, scope, redirect_uri, user_id):
        code = generate_string(self.token_length)
        expires = datetime.now() + timedelta(seconds=self.grant_expire)

        grant = self.persist_grant(client_id, code, scope, expires, redirect_uri, user_id)

        return (code ,)

    def generate_token(self, client_id, scope, refresh_token, user_id):
        if not refresh_token:
            refresh_token = generate_string(self.token_length)
        access_token = generate_string(self.token_length)
        expires = datetime.now() + timedelta(seconds=self.token_expire)

        token = self.persist_token(client_id, scope, refresh_token, access_token, expires, user_id)

        return (access_token, 'Bearer', self.token_expire, refresh_token, scope)

    def get_authorized_user(self, scopes):
        authorization = request.headers.get('Authorization')
        if self.validate_authorization_header(authorization) is False:
            raise NotAuthorized

        access_token = authorization.split()[1]
        token = self.fetch_access_token(access_token)
        if token is None:
            raise AccessDenied

        print token.expires, datetime.now()
        if token.expires < datetime.now():
            raise AccessDenied

        for scope in scopes:
            if scope not in token.get_scopes():
                raise AccessDenied

        return token.user

    def require_auth(self, *scopes):
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                user = self.get_authorized_user(scopes)
                kwargs.update(dict(user=user))
                return f(*args, **kwargs)
            return decorated
        return decorator
