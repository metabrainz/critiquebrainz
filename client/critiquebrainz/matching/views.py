from flask import Blueprint, render_template, request
from critiquebrainz.apis import musicbrainz, spotify

bp = Blueprint('matching', __name__)


@bp.route('/spotify/<uuid:release_group_id>', endpoint='spotify')
def spotify_matching_handler(release_group_id):
    release_group = musicbrainz.release_group_details(release_group_id)
    limit = 20
    offset = int(request.args.get('offset', default=0))
    response = spotify.search(release_group['title'], 'album', limit, offset).get('albums')
    count, search_results = response.get('total'), response.get('items')
    return render_template('matching/spotify.html', release_group=release_group, search_results=search_results,
                           limit=limit, offset=offset, count=count)
