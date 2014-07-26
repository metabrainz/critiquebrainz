from flask import redirect, url_for, current_app
from flask.ext.login import LoginManager, current_user
from flask.ext.babel import gettext
from provider import MusicBrainzAuthentication
from critiquebrainz.data.model.user import User
from functools import wraps

mb_auth = MusicBrainzAuthentication(
    name='musicbrainz',
    client_id=current_app.config['MUSICBRAINZ_CLIENT_ID'],
    client_secret=current_app.config['MUSICBRAINZ_CLIENT_SECRET'],
    authorize_url="https://musicbrainz.org/oauth2/authorize",
    access_token_url="https://musicbrainz.org/oauth2/token",
    base_url="https://musicbrainz.org/")


login_manager = LoginManager()
login_manager.login_view = 'login.index'
login_manager.login_message = gettext("Please sign in to access this page.")


@login_manager.user_loader
def load_user(user_id):
    return User.get(id=user_id)


def login_forbidden(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_anonymous() is False:
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated
