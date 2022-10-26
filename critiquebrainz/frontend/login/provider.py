import json

from flask import request, session, url_for
from rauth import OAuth2Service

import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.utils import generate_string


class BaseAuthentication:

    def get_authentication_uri(self, **kwargs):
        """Prepare and return uri to authentication service login form.
        All passed parameters should be included in a callback uri,
        to which user will be redirected after a successful authentication.
        """
        raise NotImplementedError

    def get_user(self):
        """Function should fetch user data from database, or, if necessary, create it, and return it."""
        raise NotImplementedError

    def validate_post_login(self):
        """Function validating parameters passed in uri query after redirection from login form.
        Should return True, if everything is ok, or False, if something went wrong.
        """
        raise NotImplementedError

    def persist_data(self, **kwargs):
        """Save data in session."""
        if self._session_key not in session:
            session[self._session_key] = dict()

        session[self._session_key].update(**kwargs)

    def fetch_data(self, key, default=None):
        """Fetch data from session."""
        if self._session_key not in session:
            return None
        return session[self._session_key].get(key, default)

    def __init__(self, name, service, session_key):
        self._name = name
        self._service = service
        self._session_key = session_key


def musicbrainz_auth_session_decoder(message):
    """Decode the json oauth response from MusicBrainz, returning {} if the response isn't valid json"""
    try:
        return json.loads(message.decode("utf-8"))
    except ValueError:
        return {}


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
        data = dict(code=str(self.fetch_data('code')),
                    grant_type='authorization_code',
                    redirect_uri=url_for('login.musicbrainz_post', _external=True))
        try:
            s = self._service.get_auth_session(
                data=data,
                decoder=musicbrainz_auth_session_decoder,
            )
            data = s.get('oauth2/userinfo').json()
            musicbrainz_id = data.get('sub')
            musicbrainz_row_id = data.get('metabrainz_user_id')
            user = db_users.get_or_create(musicbrainz_row_id, musicbrainz_id, new_user_data={
                'display_name': musicbrainz_id,
            })

            if user["musicbrainz_username"] != musicbrainz_id:
                user = db_users.update_username(user, musicbrainz_id)

            return User(user)
        except KeyError:
            return None

    def validate_post_login(self):
        if request.args.get('error'):
            return False
        if self.fetch_data('csrf') != request.args.get('state'):
            return False
        code = request.args.get('code')
        if not code:
            return False
        self.persist_data(code=code)
        return True

    def __init__(self, service=None, session_key='musicbrainz', **kwargs):
        if service is None:
            service = OAuth2Service(**kwargs)
        super(MusicBrainzAuthentication, self).__init__(kwargs.get('name'), service, session_key)
