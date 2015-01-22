from rauth import OAuth2Service
from flask import request, session, url_for
from critiquebrainz.data.model.user import User
from critiquebrainz.utils import generate_string
import json

_service = None
_session_key = None


def init(client_id, client_secret, session_key='musicbrainz'):
    global _service, _session_key
    _service = OAuth2Service(
        name='musicbrainz',
        base_url="https://musicbrainz.org/",
        authorize_url="https://musicbrainz.org/oauth2/authorize",
        access_token_url="https://musicbrainz.org/oauth2/token",
        client_id=client_id,
        client_secret=client_secret,
    )
    _session_key = session_key


def persist_data(**kwargs):
    """Save data in session."""
    if _session_key not in session:
        session[_session_key] = dict()
    session[_session_key].update(**kwargs)


def fetch_data(key, default=None):
    """Fetch data from session."""
    if _session_key not in session:
        return None
    else:
        return session[_session_key].get(key, default)


def get_authentication_uri():
    """Prepare and return uri to authentication service login form.
    All passed parameters should be included in a callback uri,
    to which user will be redirected after a successful authentication.
    """
    csrf = generate_string(20)
    persist_data(csrf=csrf)
    params = dict(response_type='code',
                  redirect_uri=url_for('login.musicbrainz_post', _external=True),
                  scope='profile rating',
                  state=csrf)
    return _service.get_authorize_url(**params)


def get_user():
    """Function should fetch user data from database, or, if necessary, create it, and return it."""
    data = dict(
        code=fetch_data('code'),
        grant_type='authorization_code',
        redirect_uri=url_for('login.musicbrainz_post', _external=True)
    )
    s = _service.get_auth_session(data=data, decoder=json.loads)
    data = s.get('oauth2/userinfo').json()
    return User.get_or_create(
        musicbrainz_id=data.get('sub'),
        display_name=data.get('sub'),
        mb_access_code=fetch_data('code'),
    )


def validate_post_login():
    """Function validating parameters passed in uri query after redirection from login form.
    Should return True, if everything is ok, or False, if something went wrong.
    """
    if request.args.get('error'):
        return False
    if fetch_data('csrf') != request.args.get('state'):
        return False
    code = request.args.get('code')
    if not code:
        return False
    persist_data(code=code)
    return True
