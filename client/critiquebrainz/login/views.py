from flask import Blueprint, request, redirect, render_template, url_for, session, flash
from flask.ext.login import login_user, logout_user, login_required
from critiquebrainz.apis import server
from critiquebrainz.login import User, login_forbidden

login_bp = Blueprint('login', __name__)


@login_bp.route('/', endpoint='index')
@login_forbidden
def login_handler():
    return render_template('login/login.html')


@login_bp.route('/musicbrainz', endpoint='musicbrainz')
@login_forbidden
def login_musicbrainz_handler():
    next = request.args.get('next')
    session['next'] = next
    return redirect(server.generate_musicbrainz_authorization_uri())


@login_bp.route('/post', endpoint='post')
@login_forbidden
def login_post_handler():
    code = request.args.get('code')
    error = request.args.get('error')
    next = session.get('next')
    if code:
        access_token, refresh_token, expires_in = server.get_token_from_auth_code(code)
        user = User(refresh_token)
        user.access_token, user.expires_in = (access_token, expires_in)
        login_user(user)
        if next:
            return redirect(next)
        else:
            return redirect(url_for('index'))
    elif error:
        flash('Login failed.', 'error')

    return redirect(url_for('.index'))


@login_bp.route('/logout', endpoint='logout')
@login_required
def login_logout_handler():
    logout_user()
    session.clear()
    return redirect(url_for('index'))
