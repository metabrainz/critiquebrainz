from flask import Blueprint, render_template
from flask import current_app
from critiquebrainz.db import users as db_users
from critiquebrainz.db.users import gravatar_url

moderators_bp = Blueprint('moderators', __name__)


@moderators_bp.route('/')
def mods_list():
    mod_usernames = set(map(str.lower, current_app.config['ADMINS']))  # MusicBrainz usernames
    mods_data = db_users.get_many_by_mb_username(list(mod_usernames))
    mods = []
    for mod_data in mods_data:
        # Removing from `mod_usernames` to figure out which mods don't have a CB account afterwards
        if mod_data["musicbrainz_id"].lower() in mod_usernames:
            mod_usernames.remove(mod_data["musicbrainz_id"].lower())
        mods.append({
            'critiquebrainz_id': mod_data["id"],
            'musicbrainz_username': mod_data["musicbrainz_id"],
            'avatar_url': gravatar_url(mod_data["musicbrainz_id"]),
        })
    for mod_username in mod_usernames:  # The rest
        mods.append({
            'musicbrainz_username': mod_username,
            'avatar_url': gravatar_url(mod_username, default="mm"),
        })
    mods = sorted(mods, key=lambda k: k['musicbrainz_username'].lower())
    return render_template('moderators/moderators.html', moderators=mods)
