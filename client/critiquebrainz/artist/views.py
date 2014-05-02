from flask import Blueprint, render_template, request
from critiquebrainz import musicbrainz


bp = Blueprint('artist', __name__)


@bp.route('/<uuid:id>', endpoint='entity')
def artist_entity_handler(id):
    artist = musicbrainz.artist_details(id)
    limit = int(request.args.get('limit', default=20))
    offset = int(request.args.get('offset', default=0))
    count, releases = musicbrainz.browse_release_groups(artist=id, limit=limit, offset=offset)
    return render_template('artist.html', id=id, artist=artist, releases=releases,
                           limit=limit, offset=offset, count=count)
