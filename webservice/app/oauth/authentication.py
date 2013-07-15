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

    def login_handler(self, f):
        """ Decorator for a login endpoint. In body of the function you may 
            specify code which will be run before redirecting to authentication 
            provider.
        """
        self._login_handler = f
        @wraps(f)
        def decorated(*args, **kwargs):
            if self.is_user():
                return redirect(url_for(self._error_handler.__name__))
            f(*args, **kwargs)
            return redirect(self.get_authentication_uri())
        return decorated

    def persist_data(self, **kwargs):
        """ Save data in session """
        if self._session_key not in session:
            session[self._session_key] = dict()
        session[self._session_key].update(**kwargs)

    def fetch_data(self, key, default=None):
        """ Fetch data from session """
        return session[self._session_key].get(key, default)

    def post_login_handler(self, f):
        """ Decorator for a post login endpoint. In body of the function 
            you should specify code which will return a relevant response
            in case there is no `next` parameter defined in uri query.
        """
        self._post_login_handler = f
        @wraps(f)
        def decorated(*args, **kwargs):
            next = request.args.get('next', None)
            try:
                self.validate_post_login()
                user = self.get_user()
                self.register_user(user)
            except AuthenticationError as e:
                flash(str(e))
                return redirect(url_for(self._error_handler.__name__,
                    next=next))

            if next:
                return redirect(next)
            else:
                return f(*args, **kwargs)
        return decorated

    def error_handler(self, f):
        self._error_handler = f
        return f

    def register_user(self, user):
        g.user = user
        session.update(user_id=user.id)

    def is_user(self):
        try:
            return g.user is not None
        except:
            return False

    def __init__(self, service, session_key):
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
            raise AuthenticationError('Could not access data from Twitter')

        twitter_id = data.get('id_str')
        display_name = data.get('screen_name')

        # user lookup
        user = User.query.filter_by(twitter_id=twitter_id).first()

        if user is None:
            # if no user found, create a new one
            user = User(display_name=display_name, twitter_id=twitter_id)
            db.session.add(user)
            db.session.commit()
            
        return user

    def validate_post_login(self):
        if 'denied' in request.args:
            raise AuthenticationError('You did not authorize the request')

        oauth_token = request.args.get('oauth_token', None)
        oauth_verifier = request.args.get('oauth_verifier', None)

        if oauth_token is None or oauth_verifier is None:
            return AuthenticationError

        request_token = self.fetch_data('request_token')
        request_token_secret = self.fetch_data('request_token_secret')

        if request_token is None or request_token_secret is None:
            raise AuthenticationError

        if request_token != oauth_token:
            raise AuthenticationError

        # persist verifier
        self.persist_data(oauth_verifier=oauth_verifier)

    def __init__(self, service=None, session_key='twitter', **kwargs):
        if service is None:
            service = OAuth1Service(**kwargs)
        super(TwitterAuthentication,self).__init__(service, session_key)

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
            raise AuthenticationError('Could not access data from MusicBrainz')

        musicbrainz_id = data.get('sub')
        display_name = data.get('sub')

        # user lookup
        user = User.query.filter_by(musicbrainz_id=musicbrainz_id).first()

        if user is None:
            # if no user found, create a new one
            user = User(display_name=display_name,
                email=email, 
                musicbrainz_id=musicbrainz_id)
            db.session.add(user)
            db.session.commit()
            
        return user

    def validate_post_login(self):
        state = request.args.get('state', None)
        if state != self.fetch_data('csrf'):
            raise AuthenticationError

        error = request.args.get('error', None)
        if error is not None:
            if error == 'access_denied':
                raise AuthenticationError('You did not authorize the request')
            else:
                raise AuthenticationError

        code = request.args.get('code', None)
        if code is None:
            raise AuthenticationError
        self.persist_data(code=code)

    def __init__(self, service=None, session_key='musicbrainz', **kwargs):
        if service is None:
            service = OAuth2Service(**kwargs)
        super(MusicBrainzAuthentication, self).__init__(service, session_key)