from flask import Blueprint, request, redirect, render_template, url_for, session, flash, current_app
from flask.ext.login import login_user, logout_user, login_required
from flask.ext.babel import gettext
from critiquebrainz.frontend.login import login_forbidden
from . import mb_auth

login_bp = Blueprint('login', __name__)


@login_bp.route('/', endpoint='index')
@login_forbidden
def login_handler():
    return render_template('login/login.html')


@login_bp.route('/musicbrainz', endpoint='musicbrainz')
@login_forbidden
def mb_oauth():
    session['next'] = request.args.get('next')
    return redirect(mb_auth.get_authentication_uri())


@login_bp.route('/musicbrainz/post', endpoint='musicbrainz_post')
@login_forbidden
def mb_oauth_callback():
    if mb_auth.validate_post_login():
        login_user(mb_auth.get_user())
        next = session.get('next')
        if next:
            return redirect(next)
    else:
        flash(gettext("Login failed."), 'error')
    return redirect(url_for('frontend.index'))


@login_bp.route('/logout', endpoint='logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))
