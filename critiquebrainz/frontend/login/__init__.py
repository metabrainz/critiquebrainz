"""
Package login provides authentication functionality for CritiqueBrainz.

It is based on OAuth2 protocol. MusicBrainz is the only supported provider.
"""
from flask import redirect, url_for
from flask_login import LoginManager, current_user
from flask_babel import lazy_gettext
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.mixins import AnonymousUser
from werkzeug.exceptions import Unauthorized
from functools import wraps

mb_auth = None

login_manager = LoginManager()
login_manager.login_view = 'login.index'
login_manager.login_message = lazy_gettext(u"Please sign in to access this page.")
login_manager.localize_callback = lazy_gettext
login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.get(id=user_id)


def login_forbidden(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_anonymous() is False:
            return redirect(url_for('frontend.index'))
        return f(*args, **kwargs)

    return decorated


def admin_view(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            raise Unauthorized(lazy_gettext('You must be an administrator to view this page.'))
        return f(*args, **kwargs)

    return decorated
