from flask import request, session, redirect, flash, url_for, g
from rauth import OAuth1Service, OAuth2Service
from app import db
from app.models import User
from app.exceptions import *
from functools import wraps

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

    def authorize_handler(self, f):
        """ Decorator for an authorization endpoint.
        """
        self._authorize_handler = f
        @wraps(f)
        def decorated(provider, *args, **kwargs):
            user_id = self.fetch_data('user_id')

            if provider == self._name:
                user_id = self.fetch_data('user_id')
                if user_id is None:
                    self.persist_data(args=request.args.to_dict())
                    try:
                        return redirect(self.get_authentication_uri())
                    except:
                        AuthorizationError
                else:
                    user = User.query.get(user_id)
                    g.user = user
                    if request.method == 'POST':
                        # wipe session after user's decision
                        session.pop(self._session_key, None)
            else:
                session.pop(self._session_key, None)

            return f(provider, *args, **kwargs)
        return decorated

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

    def post_login_handler(self, f):
        """ Decorator for a post login endpoint. In body of the function 
            you should specify code which will be run before redirecting
            to authorization endpoint.
        """
        self._post_login_handler = f
        @wraps(f)
        def decorated(*args, **kwargs):
            self.validate_post_login()

            user = self.get_user()
            self.persist_data(user_id=user.id)

            f(*args, **kwargs)

            args = self.fetch_data('args')
            if args is None:
                raise AuthorizationError
            return redirect(url_for(self._authorize_handler.__name__, 
                provider=self._name, **args))
        return decorated

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
        oauth_callback = url_for(self._post_login_handler.__name__, 
            _external=True, **kwargs)
        request_token, _ = self.new_request_token(oauth_callback=oauth_callback)
        return self._service.get_authorize_url(request_token)

    def get_user(self):
        oauth_verifier = self.fetch_data('oauth_verifier')
        request_token = self.fetch_data('request_token')
        request_token_secret = self.fetch_data('request_token_secret')

        # start API session and fetch the data
        try:
            s = self._service.get_auth_session(request_token, request_token_secret, 
                method='POST', data={'oauth_verifier': oauth_verifier})
            data = s.get('account/verify_credentials.json').json()
        except:
            raise AuthorizationError

        twitter_id = data.get('id_str')
        display_name = data.get('screen_name')

        user = User.get_or_create(display_name, twitter_id=twitter_id)
            
        return user

    def validate_post_login(self):
        if 'denied' in request.args:
            try:
                redirect_uri = self.fetch_data('args').get('redirect_uri')
            except:
                redirect_uri = None
            raise AuthorizationError('access_denied', redirect_uri)

        oauth_token = request.args.get('oauth_token', None)
        oauth_verifier = request.args.get('oauth_verifier', None)

        if oauth_token is None or oauth_verifier is None:
            return AuthorizationError

        request_token = self.fetch_data('request_token')
        request_token_secret = self.fetch_data('request_token_secret')

        if request_token is None or request_token_secret is None:
            raise AuthorizationError

        if request_token != oauth_token:
            raise AuthorizationError

        # persist verifier
        self.persist_data(oauth_verifier=oauth_verifier)

    def __init__(self, service=None, session_key='twitter', **kwargs):
        if service is None:
            service = OAuth1Service(**kwargs)
        super(TwitterAuthentication,self).__init__(kwargs.get('name'), 
            service, session_key)

class MusicBrainzAuthentication(BaseAuthentication):

    def generate_csrf(self, length=10):
        import random
        string = ''.join(random.choice('0123456789ABCDEF') for i in range(length))
        return string
  
    def get_authentication_uri(self, **kwargs):
        csrf = self.generate_csrf()
        self.persist_data(csrf=csrf)
        params = dict(response_type='code',
            redirect_uri=url_for(self._post_login_handler.__name__, _external=True),
            scope='profile',
            state=csrf)
        return self._service.get_authorize_url(**params)

    def get_user(self):
        import json
        data = dict(code=self.fetch_data('code'),
                    grant_type='authorization_code',
                    redirect_uri=url_for(self._post_login_handler.__name__, _external=True))
        try:
            r = self._service.get_raw_access_token(data=data).json()
            s = self._service.get_session(r['access_token'])
            data = s.get('oauth2/userinfo').json()
        except:
            raise AuthorizationError

        musicbrainz_id = data.get('sub')
        display_name = data.get('sub')

        user = User.get_or_create(display_name, musicbrainz_id=musicbrainz_id)
            
        return user

    def validate_post_login(self):
        state = request.args.get('state', None)
        if state != self.fetch_data('csrf'):
            raise AuthorizationError

        error = request.args.get('error', None)
        if error == 'access_denied':
            try:
                redirect_uri = self.fetch_data('args').get('redirect_uri')
            except:
                redirect_uri = None
            raise AuthorizationError('access_denied', redirect_uri)
        elif error is not None:
            raise AuthorizationError

        code = request.args.get('code', None)
        if code is None:
            raise AuthorizationError

        self.persist_data(code=code)

    def __init__(self, service=None, session_key='musicbrainz', **kwargs):
        if service is None:
            service = OAuth2Service(**kwargs)
        super(MusicBrainzAuthentication, self).__init__(kwargs.get('name'), 
            service, session_key)