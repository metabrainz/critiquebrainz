from flask import Blueprint, render_template, request
from critiquebrainz import musicbrainz
from critiquebrainz.api import api


bp = Blueprint('artist', __name__)


@bp.route('/<uuid:id>', endpoint='entity')
def artist_entity_handler(id):
    artist = musicbrainz.artist_details(id)
    release_type = request.args.get('release_type', default='album')
    limit = int(request.args.get('limit', default=30))
    offset = int(request.args.get('offset', default=0))
    count, releases = musicbrainz.browse_release_groups(artist=id, release_type=release_type,
                                                        limit=limit, offset=offset)
    for release in releases:
        review_count, reviews = api.get_reviews(release_group=release['id'], sort='created', limit=1)
        release['review_count'] = review_count
    return render_template('artist.html', id=id, artist=artist, release_type=release_type, releases=releases,
                           limit=limit, offset=offset, count=count)
