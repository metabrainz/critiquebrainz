from flask import Blueprint, request, redirect, render_template, url_for, session
from flask_babel import gettext
from flask_login import login_user, logout_user, login_required

from critiquebrainz.frontend import flash
from critiquebrainz.frontend.login import mb_auth, login_forbidden

login_bp = Blueprint('login', __name__)


@login_bp.route('/')
@login_forbidden
def index():
    return render_template('login/index.html')


@login_bp.route('/musicbrainz')
@login_forbidden
def musicbrainz():
    session['next'] = request.args.get('next')
    return redirect(mb_auth.get_authentication_uri())


@login_bp.route('/musicbrainz/post')
@login_forbidden
def musicbrainz_post():
    """Callback endpoint."""
    if mb_auth.validate_post_login():
        user = mb_auth.get_user()
        if user:
            login_user(user)
            next = session.get('next')
            if next:
                return redirect(next)
        else:
            flash.error(gettext("Login failed."))
    else:
        flash.error(gettext("Login failed."))
    return redirect(url_for('frontend.index'))


@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    next = request.args.get('next')
    if next:
        return redirect(next)
    return redirect(url_for('frontend.index'))
