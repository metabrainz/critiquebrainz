from flask import Blueprint, render_template
from flask import current_app
from critiquebrainz.db import users as db_users

moderators_bp = Blueprint('moderators', __name__)


@moderators_bp.route('/')
def moderators():
    admins = current_app.config['ADMINS']
    db_admins = db_users.get_many_by_mb_username(admins)
    user_names = [item['display_name'] for item in db_admins]
    # list of MB users without CritiqueBrainz account
    no_auth = list(set(admins) - set(user_names))
    if user_names != admins:
        for item in no_auth:  # Add them to the main list of admins
            user = {'display_name': item, 'musicbrainz_id': None,
                    'avatar_url': 'https://gravatar.com/avatar/'}
            db_admins.append(user)
    return render_template('moderators/moderators.html', db_admins=db_admins)
