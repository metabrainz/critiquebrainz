from flask import Blueprint, render_template
from flask import current_app
from critiquebrainz.db import users as db_users
from critiquebrainz.db.users import avatar

moderators_bp = Blueprint('moderators', __name__)


@moderators_bp.route('/')
def moderators():
    admins = current_app.config['ADMINS']
    moderators = db_users.get_many_by_mb_username(admins)
    usernames = [moderator['display_name'] for moderator in moderators]
    # list of MB users without CritiqueBrainz account
    missing_users = list(set(admins) - set(usernames))
    if missing_users:
        for user in missing_users:  # Add them to the main list of admins
            moderators.append({'musicbrainz_id': user,
                               'avatar_url': avatar(user),
                               })
    return render_template('moderators/moderators.html', moderators=moderators)
