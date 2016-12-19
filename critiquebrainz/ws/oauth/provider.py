from flask import request
from datetime import datetime, timedelta
from functools import wraps

from critiquebrainz.data import db
from critiquebrainz.data.model.oauth_client import OAuthClient
from critiquebrainz.data.model.oauth_grant import OAuthGrant
from critiquebrainz.data.model.oauth_token import OAuthToken
from critiquebrainz.ws.constants import available_scopes
from critiquebrainz.ws.exceptions import NotAuthorized
from critiquebrainz.ws.oauth import exceptions
from critiquebrainz.utils import generate_string


class CritiqueBrainzAuthorizationProvider(object):

    def init_app(self, app):
        self.token_length = app.config['OAUTH_TOKEN_LENGTH']
        self.grant_expire = app.config['OAUTH_GRANT_EXPIRE']
        self.token_expire = app.config['OAUTH_TOKEN_EXPIRE']

    @staticmethod
    def validate_authorization_header(value):
        if not value or isinstance(value, str) is False:
            return False

        authorization = value.split()
        if len(authorization) != 2:
            return False

        if authorization[0] != 'Bearer':
            return False

        return True

    @staticmethod
    def validate_client_id(client_id):
        if not client_id:
            return False
        return OAuthClient.query.get(client_id) is not None

    @staticmethod
    def validate_client_secret(client_id, client_secret):
        client = OAuthClient.query.get(client_id)
        if client is None:
            return False
        else:
            return client.client_secret == client_secret

    @staticmethod
    def validate_client_redirect_uri(client_id, redirect_uri):
        client = OAuthClient.query.get(client_id)

        if client is None or isinstance(redirect_uri, str) is False:
            return False
        else:
            return client.redirect_uri == redirect_uri.split('?')[0]

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
        return (datetime.now() > grant.expires) is False

    def validate_token_scope(self, client_id, refresh_token, scope):
        token = self.fetch_token(client_id, refresh_token)
        return self.validate_scope(scope, token.get_scopes())

    def validate_token(self, client_id, refresh_token):
        return self.fetch_token(client_id, refresh_token) is not None

    @staticmethod
    def validate_scope(scope, valid_scopes=available_scopes):
        if not scope or isinstance(scope, str) is False:
            return False

        scopes = scope.split()
        for scope in scopes:
            if scope not in valid_scopes:
                return False
        return True

    @staticmethod
    def persist_grant(client_id, code, scopes, expires, redirect_uri, user_id):
        grant = OAuthGrant(client_id=client_id,
                           code=code,
                           scopes=scopes,
                           expires=expires,
                           redirect_uri=redirect_uri,
                           user_id=user_id)
        db.session.add(grant)
        db.session.commit()
        return grant

    @staticmethod
    def persist_token(client_id, scope, refresh_token, access_token, expires, user_id):
        token = OAuthToken(client_id=client_id,
                           scopes=scope,
                           access_token=access_token,
                           refresh_token=refresh_token,
                           expires=expires,
                           user_id=user_id)

        db.session.add(token)
        db.session.commit()
        return token

    @staticmethod
    def fetch_grant(client_id, code):
        grant = OAuthGrant.query.filter_by(client_id=client_id, code=code).first()
        return grant

    @staticmethod
    def fetch_token(client_id, refresh_token):
        token = OAuthToken.query.filter_by(client_id=client_id, refresh_token=refresh_token).first()
        return token

    @staticmethod
    def fetch_access_token(access_token):
        token = OAuthToken.query.filter_by(access_token=access_token).first()
        return token

    @staticmethod
    def discard_grant(client_id, code):
        OAuthGrant.query.filter_by(client_id=client_id, code=code).delete()

    @staticmethod
    def discard_token(client_id, refresh_token):
        OAuthToken.query.filter_by(client_id=client_id, refresh_token=refresh_token).delete()

    @staticmethod
    def discard_client_user_tokens(client_id, user_id):
        OAuthToken.query.filter_by(client_id=client_id, user_id=user_id).delete()

    def validate_authorization_request(self, client_id, response_type, redirect_uri, scope=None):
        if self.validate_client_id(client_id) is False:
            raise exceptions.InvalidClient
        if response_type != 'code':
            raise exceptions.UnsupportedResponseType
        if self.validate_client_redirect_uri(client_id, redirect_uri) is False:
            raise exceptions.InvalidRedirectURI
        if scope and not self.validate_scope(scope):
            raise exceptions.InvalidScope

    def validate_token_request(self, grant_type, client_id, client_secret, redirect_uri, code, refresh_token):
        if self.validate_client_id(client_id) is False:
            raise exceptions.InvalidClient
        if self.validate_client_secret(client_id, client_secret) is False:
            raise exceptions.InvalidClient
        if grant_type == 'authorization_code':
            if self.validate_grant(client_id, code) is False:
                raise exceptions.InvalidGrant
            if self.validate_grant_redirect_uri(client_id, code, redirect_uri) is False:
                raise exceptions.InvalidRedirectURI
        elif grant_type == 'refresh_token':
            if self.validate_token(client_id, refresh_token) is False:
                raise exceptions.InvalidGrant
        else:
            raise exceptions.UnsupportedGrantType

    def generate_grant(self, client_id, user_id, redirect_uri, scope=None):
        code = generate_string(self.token_length)
        expires = datetime.now() + timedelta(seconds=self.grant_expire)
        grant = self.persist_grant(client_id, code, scope, expires, redirect_uri, user_id)
        return code

    def generate_token(self, client_id, refresh_token, user_id, scope=None):
        if not refresh_token:
            refresh_token = generate_string(self.token_length)
        access_token = generate_string(self.token_length)
        expires = datetime.now() + timedelta(seconds=self.token_expire)

        token = self.persist_token(client_id, scope, refresh_token, access_token, expires, user_id)

        return access_token, 'Bearer', self.token_expire, refresh_token

    def get_authorized_user(self, scopes):
        authorization = request.headers.get('Authorization')
        if self.validate_authorization_header(authorization) is False:
            raise NotAuthorized

        access_token = authorization.split()[1]
        token = self.fetch_access_token(access_token)
        if token is None:
            raise exceptions.InvalidToken

        if token.expires < datetime.now():
            raise exceptions.InvalidToken

        for scope in scopes:
            if scope not in token.get_scopes():
                raise exceptions.InvalidToken

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
