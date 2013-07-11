from flask import g
from rauth import OAuth1Service, OAuth2Service
from pyoauth2.provider import AuthorizationProvider
from datetime import datetime, timedelta
from app import app, db
from app.models import OAuthClient, OAuthAuthorizationCode, OAuthAccessToken,\
                       OAuthRefreshToken

# authentication providers

twitter = OAuth1Service(
    consumer_key=app.config['TWITTER_CONSUMER_KEY'],
    consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
    name='twitter',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    request_token_url='https://api.twitter.com/oauth/request_token',
    base_url='https://api.twitter.com/1.1/')
    
musicbrainz = OAuth2Service(
    client_id='gn_M5vKGjZDw55CiRpCKvA',
    client_secret='QVyZm7oXIbfIx5_e-S9ZyQ',
    name='musicbrainz',
    authorize_url='https://musicbrainz.org/oauth2/authorize',
    access_token_url='https://musicbrainz.org/oauth2/token',
    base_url='https://musicbrainz.org/')

# authorization provider

class CritiqueBrainzAuthorizationProvider(AuthorizationProvider):
    """ OAuth 2.0 provider class. """

    def validate_client_id(self, client_id):
        """ Check that the client_id represents a valid client. """
        if client_id is None: return False
        return OAuthClient.query.get(client_id) is not None

    def validate_client_secret(self, client_id, client_secret):
        """ Check that the passed secret matches the client secret. """
        client = OAuthClient.query.get(client_id)
        if client is not None and client.secret == client_secret:
            return True
        else:
            return False

    def validate_redirect_uri(self, client_id, redirect_uri):
        """ Validate that the redirect_uri requested is available for the client. """
        if redirect_uri is None: return False
        client = OAuthClient.query.get(client_id)
        if client is not None and client.redirect_uri == redirect_uri.split('?')[0]:
            return True
        else:
            return False

    def validate_access(self):
        """ Validate that an OAuth token can be generated from the recent
            authentication. 
        """
        return g.user is not None

    def validate_scope(self, client_id, scope):
        """ Validate that the scope requested is available for the client. """
        if scope == None or scope == '' or scope == 'all':
            return True
        else:
            return False

    def persist_authorization_code(self, client_id, code, scope):
        """ Store important session information (user_id) along with the
            authorization code to later allow an access token to be created. 
        """
        client = OAuthClient.query.get(client_id)
        user = g.user
        if client is not None and user is not None:
            authorization_code = OAuthAuthorizationCode(code, client, user, scope)
            db.session.add(authorization_code)
            db.session.commit()

    def persist_token_information(self, client_id, scope, access_token,
                                  token_type, expires_in, refresh_token,
                                  data):
        """ Store OAuth access and refresh token. """
        client = OAuthClient.query.get(client_id)
        user = g.user
        expire = datetime.now() + timedelta(seconds=expires_in)
        oauth_access_token = OAuthAccessToken(access_token, client, user, scope, expire)
        oauth_refresh_token = OAuthRefreshToken(refresh_token, client, user, scope)
        db.session.add(oauth_access_token)
        db.session.add(oauth_refresh_token)
        db.session.commit()

    def from_authorization_code(self, client_id, code, scope):
        """ Get session data from authorization code. """
        authorization_code = OAuthAuthorizationCode.query.get(code)
        if authorization_code is not None:
            # validate scope and client_id
            if client_id == authorization_code.client_id and\
                scope == authorization_code.scope:
                resp = {'client_id': authorization_code.client_id,
                        'scope': authorization_code.scope,
                        'user_id': authorization_code.user_id}
                return resp

        return None

    def from_refresh_token(self, client_id, refresh_token, scope):
        """ Get session data from refresh token. """
        oauth_refresh_token = OAuthRefreshToken.query.get(refresh_token)
        if oauth_refresh_token is not None:
            # validate scope and client_id
            if client_id == oauth_refresh_token.client_id and\
                ( scope == '' or scope == 'all' ):
                resp = {'client_id': oauth_refresh_token.client_id,
                        'scope': oauth_refresh_token.scope,
                        'user_id': oauth_refresh_token.user_id}
                return resp

        return None

    def discard_authorization_code(self, client_id, code):
        """ Delete authorization code from the store. """
        authorization_code = OAuthAuthorizationCode.query.get(code)
        db.session.delete(authorization_code)
        db.session.commit()

    def discard_refresh_token(self, client_id, refresh_token):
        """ Delete refresh token from the store. """
        oauth_refresh_token = OAuthRefreshToken.query.get(refresh_token)
        db.session.delete(oauth_refresh_token)
        db.session.commit()

    def discard_client_user_tokens(self, client_id, user_id):
        """ Delete access and refresh tokens from the store. """
        db.session.query(OAuthRefreshToken).\
            filter(db._and(
                OAuthRefreshToken.client_id == client_id,
                OAuthRefreshToken.user_id == user_id)
            ).delete()
        db.session.query(OAuthAccessToken).\
            filter(db._and(
                OAuthAccessToken.client_id == client_id,
                OAuthAccessToken.user_id == user_id)
            ).delete()
        db.session.commit()

oauth_provider = CritiqueBrainzAuthorizationProvider()