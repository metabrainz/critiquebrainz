from flask.ext.login import LoginManager, UserMixin, current_user
from flask import redirect, url_for, session
from critiquebrainz.api import api
from critiquebrainz.exceptions import SessionError
from functools import wraps
from datetime import datetime
import time
import json

login_manager = LoginManager()
login_manager.login_view = 'login.index'

@login_manager.user_loader
def load_user(refresh_token):
    return User(refresh_token)

class User(UserMixin):

    def get_id(self):
        return self.refresh_token

    def __init__(self, refresh_token):
        self.refresh_token = refresh_token

    def regenerate_token(self):
        try:
            access_token, _, expires_in = api.get_token_from_refresh_token(self.refresh_token)
        except APIError:
            raise SessionError

        self.access_token = access_token
        self.expires_in = expires_in

    @property
    def me(self):
        if hasattr(self, '_me') is False:
            self._me = api.get_me(self.access_token)
        return self._me

    @property
    def access_token(self):
        if self.expires_in < datetime.now():
            self.regenerate_token()
        return session.get('access_token')

    @access_token.setter
    def access_token(self, value):
        session['access_token'] = value

    @property
    def expires_in(self):
        return datetime.fromtimestamp(session.get('expires_in'))

    @expires_in.setter
    def expires_in(self, value):
        session['expires_in'] = time.time() + int(value)
    
def login_forbidden(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_anonymous() is False:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated
