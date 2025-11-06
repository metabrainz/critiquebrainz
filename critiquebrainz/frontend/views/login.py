from flask import Blueprint, request, redirect, render_template, url_for, session, current_app
from flask_babel import gettext
from flask_login import login_user, logout_user, login_required

import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.frontend import flash
from critiquebrainz.frontend.login import login_forbidden, oauth

login_bp = Blueprint('login', __name__)


@login_bp.route('/')
@login_forbidden
def index():
    return render_template('login/index.html')


@login_bp.route('/musicbrainz')
@login_forbidden
def musicbrainz():
    session['next'] = request.args.get('next')
    login_hint = request.args.get("login_hint")
    kwargs = {
        "redirect_uri": url_for('login.musicbrainz_post', _external=True),
    }
    if login_hint:
        kwargs["login_hint"] = login_hint
    return oauth.musicbrainz.authorize_redirect(**kwargs)


@login_bp.route('/musicbrainz/post')
@login_forbidden
def musicbrainz_post():
    """Callback endpoint."""
    try:
        token = oauth.musicbrainz.authorize_access_token()
        response = oauth.musicbrainz.post(
            f"{current_app.config['MUSICBRAINZ_OAUTH_URL']}/introspect",
            data={
                "client_id": current_app.config["MUSICBRAINZ_CLIENT_ID"],
                "client_secret": current_app.config["MUSICBRAINZ_CLIENT_SECRET"],
                "token": token["access_token"],
                "token_type_hint": "access_token",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        info = response.json()

        musicbrainz_id = info["sub"]
        musicbrainz_row_id = info["metabrainz_user_id"]
        user = db_users.get_or_create(musicbrainz_row_id, musicbrainz_id, new_user_data={
            'display_name': musicbrainz_id,
        })

        if user["musicbrainz_username"] != musicbrainz_id:
            user = db_users.update_username(user, musicbrainz_id)

        login_user(User(user))
        next = session.get('next')
        if next:
            return redirect(next)
    except Exception as e:
        current_app.logger.exception("Login failed: %s", e)
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
