from flask import request, session, redirect, flash, url_for, g
from rauth import OAuth1Service, OAuth2Service
from critiquebrainz.db import db, User
from critiquebrainz.exceptions import LoginError
from critiquebrainz.utils import generate_string
from functools import wraps
import json

class BaseAuthentication(object):

    def get_authentication_uri(self, **kwargs):
        """ Prepare and return uri to authentication service login form.
            All passed parameters should be included in a callback uri,
            to which user will be redirected after a successful authentication 
        """
        raise NotImplementedError

    def get_user(self):
        """ Function should fetch user data from database, or, if necessary,
            create it, and return it.
        """
        raise NotImplementedError

    def validate_post_login(self):
        """ Function validating parameters passed in uri query after
            redirection from login form. Should return True, if everything
            is ok, or False, if something went wrong.
        """
        raise NotImplementedError

    def persist_data(self, **kwargs):
        """ Save data in session """
        if self._session_key not in session:
            session[self._session_key] = dict()

        session[self._session_key].update(**kwargs)

    def fetch_data(self, key, default=None):
        """ Fetch data from session """
        if self._session_key not in session:
            return None
        else:
            return session[self._session_key].get(key, default)

    def __init__(self, name, service, session_key):
        self._name = name
        self._service = service
        self._session_key = session_key

class TwitterAuthentication(BaseAuthentication):

    def new_request_token(self, persist=True, **kwargs):
        # fetch request token from twitter
        request_token, request_token_secret = self._service.get_request_token(
            params=kwargs)
        # persist tokens in session
        if persist is True:
            self.persist_data(request_token=request_token,
                request_token_secret=request_token_secret)
        return request_token, request_token_secret

    def get_authentication_uri(self, **kwargs):
        oauth_callback = url_for('login.twitter_post', _external=True, **kwargs)
        request_token, _ = self.new_request_token(oauth_callback=oauth_callback)
        return self._service.get_authorize_url(request_token)

    def get_user(self):
        oauth_verifier = self.fetch_data('oauth_verifier')
        request_token = self.fetch_data('request_token')
        request_token_secret = self.fetch_data('request_token_secret')

        # start API session and fetch the data
        s = self._service.get_auth_session(request_token, request_token_secret, 
            method='POST', data={'oauth_verifier': oauth_verifier})
        data = s.get('account/verify_credentials.json').json()

        twitter_id = data.get('id_str')
        display_name = data.get('screen_name')

        user = User.get_or_create(display_name, twitter_id=twitter_id)
            
        return user

    def validate_post_login(self):
        request_token = self.fetch_data('request_token')
        request_token_secret = self.fetch_data('request_token_secret')
        oauth_token= request.args.get('oauth_token')
        oauth_verifier = request.args.get('oauth_verifier')
        denied = request.args.get('denied')
        
        if denied:
            if denied == request_token:
                raise LoginError('access_denied')
            else:
                raise LoginError('server_error')

        if oauth_token != request_token:
            raise LoginError('server_error')

        self.persist_data(oauth_verifier=oauth_verifier)

    def __init__(self, service=None, session_key='twitter', **kwargs):
        if service is None:
            service = OAuth1Service(**kwargs)
        super(TwitterAuthentication,self).__init__(kwargs.get('name'), 
            service, session_key)

class MusicBrainzAuthentication(BaseAuthentication):
  
    def get_authentication_uri(self, **kwargs):
        csrf = generate_string(20)
        self.persist_data(csrf=csrf)
        params = dict(response_type='code',
                      redirect_uri=url_for('login.musicbrainz_post', _external=True),
                      scope='profile',
                      state=csrf)
        return self._service.get_authorize_url(**params)

    def get_user(self):
        data = dict(code=self.fetch_data('code'),
                    grant_type='authorization_code',
                    redirect_uri=url_for('login.musicbrainz_post', _external=True))

        s = self._service.get_auth_session(data=data, decoder=json.loads)
        data = s.get('oauth2/userinfo').json()

        musicbrainz_id = data.get('sub')
        display_name = data.get('sub')

        user = User.get_or_create(display_name, musicbrainz_id=musicbrainz_id)
            
        return user

    def validate_post_login(self):
        csrf = self.fetch_data('csrf')
        error = request.args.get('error')
        code = request.args.get('code')

        if csrf != request.args.get('state'):
            raise LoginError('server_error')

        if error:
            raise LoginError('access_denied')
        
        if not code:
            raise LoginError('server_error')

        self.persist_data(code=code)

    def __init__(self, service=None, session_key='musicbrainz', **kwargs):
        if service is None:
            service = OAuth2Service(**kwargs)
        super(MusicBrainzAuthentication, self).__init__(kwargs.get('name'), 
            service, session_key)
