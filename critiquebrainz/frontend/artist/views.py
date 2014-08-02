from flask import Blueprint, render_template, request, redirect, url_for
from flask.ext.babel import gettext
from werkzeug.exceptions import BadRequest
from critiquebrainz.frontend.apis import musicbrainz
from critiquebrainz.exceptions import NotFound
from critiquebrainz.data.model.review import Review

artist_bp = Blueprint('artist', __name__)


@artist_bp.route('/<uuid:id>', endpoint='entity')
def artist_entity_handler(id):
    artist = musicbrainz.get_artist_by_id(id, includes=['url-rels', 'artist-rels'])
    if not artist:
        raise NotFound(gettext("Sorry, we couldn't find an artist with that MusicBrainz ID."))
    release_type = request.args.get('release_type', default='album')
    if release_type not in ['album', 'single', 'ep', 'broadcast', 'other']:  # supported release types
        raise BadRequest

    page = int(request.args.get('page', default=1))
    if page < 1:
        return redirect(url_for('.reviews'))
    limit = 20
    offset = (page - 1) * limit
    count, release_groups = musicbrainz.browse_release_groups(artist_id=id, release_types=[release_type],
                                                              limit=limit, offset=offset)
    for release_group in release_groups:
        # TODO: Count reviews instead of fetching them
        reviews, review_count = Review.list(release_group=release_group['id'], sort='created', limit=1)
        release_group['review_count'] = review_count
    return render_template('artist.html', id=id, artist=artist, release_type=release_type,
                           release_groups=release_groups, page=page, limit=limit, count=count)
