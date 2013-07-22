from flask_oauthlib.client import OAuth
from flask.ext.login import LoginManager, current_user
from flask import redirect, url_for
from functools import wraps

oauth = OAuth()
login_manager = LoginManager()
login_manager.login_view = 'login.index'

@login_manager.user_loader
def load_user(userid):
	from critiquebrainz.db import User
	return User.query.get(userid)

def init_app(app):
    oauth.init_app(app)
    login_manager.init_app(app)
    return (oauth, login_manager)

def login_forbidden(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		if current_user.is_anonymous() is False:
			return redirect(url_for('ui.index'))
		return f(*args, **kwargs)
	return decorated