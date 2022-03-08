from flask import Blueprint, redirect
from flask_babel import gettext
from werkzeug.exceptions import NotFound

import critiquebrainz.frontend.external.musicbrainz_db.release as mb_release

release_bp = Blueprint('release', __name__)


@release_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    release_data = mb_release.get_release_by_mbid(id)
    if release_data:
        group_id = release_data['release-group']['mbid']
        url = '/release-group/' + str(group_id)
        return redirect(url, 301)

    raise NotFound(gettext("Sorry, we couldn't find a release with that MusicBrainz ID."))
