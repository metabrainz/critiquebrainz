from flask import Blueprint, redirect
from critiquebrainz.frontend.apis import musicbrainz
from werkzeug.exceptions import NotFound

release_bp = Blueprint('release', __name__)


@release_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    if musicbrainz.get_release_by_id(id):
        release_data = musicbrainz.get_release_by_id(id)
        group_id = release_data['release-group']['id']
        url = '/release-group/' + str(group_id)
        return redirect(url, 301)
    else:
        raise NotFound(gettext("Sorry, we couldn't find a release with that MusicBrainz ID."))
