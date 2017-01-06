from flask import Blueprint, render_template
from flask import current_app
from critiquebrainz.db import users as db_users

moderators_bp = Blueprint('moderators', __name__)


@moderators_bp.route('/')
def moderators():
    admins = current_app.config['ADMINS']
    db_admins = db_users.getusers_id(admins)
    db_admins = [dict(_) for _ in db_admins]
    user_names = [_['display_name'] for _ in db_admins]
    no_auth = list(set(admins) - set(user_names))
    if user_names != admins:
        for item in no_auth:
            user = {'display_name': item, 'musicbrainz_id': None}
            db_admins.append(user)
    return render_template('moderators/moderators.html', db_admins=db_admins)
