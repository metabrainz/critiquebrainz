from flask import Blueprint, render_template, request
from werkzeug.exceptions import BadRequest

from critiquebrainz import musicbrainz
from critiquebrainz.api import api

bp = Blueprint('artist', __name__)


@bp.route('/<uuid:id>', endpoint='entity')
def artist_entity_handler(id):
    artist = musicbrainz.get_artist_by_id(id, rels=['url-rels', 'artist-rels'])
    allowed_release_types = ['album', 'single', 'ep', 'broadcast', 'other']
    release_type = request.args.get('release_type', default='album')
    if release_type not in allowed_release_types:
        raise BadRequest
    offset = int(request.args.get('offset', default=0))
    limit = 30
    count, release_groups = musicbrainz.browse_release_groups(artist_id=id, release_type=release_type,
                                                              limit=limit, offset=offset)
    for release_group in release_groups:
        review_count, reviews = api.get_reviews(release_group=release_group['id'], sort='created', limit=1)
        release_group['review_count'] = review_count
    return render_template('artist.html', id=id, artist=artist, release_type=release_type,
                           release_groups=release_groups, limit=limit, offset=offset, count=count)
