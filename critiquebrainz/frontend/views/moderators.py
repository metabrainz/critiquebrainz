from hashlib import md5
from flask import Blueprint, render_template
from flask import current_app
from critiquebrainz.db import users as db_users

moderators_bp = Blueprint('moderators', __name__)


@moderators_bp.route('/')
def moderators():
    admins = current_app.config['ADMINS']
    moderators = db_users.get_many_by_mb_username(admins)
    config_list = [moderator['display_name'] for moderator in moderators]
    # list of MB users without CritiqueBrainz account
    missing_users = list(set(admins) - set(config_list))
    if config_list != admins:
        for user in missing_users:  # Add them to the main list of admins
            url = "https://gravatar.com/avatar/{0}{1}" \
                .format(md5(user.encode('utf-8')).hexdigest(), "?d=identicon")
            user = {'display_name': user,
                    'musicbrainz_id': None,
                    'avatar_url': url,
                    }
            moderators.append(user)
    return render_template('moderators/moderators.html', moderators=moderators)
