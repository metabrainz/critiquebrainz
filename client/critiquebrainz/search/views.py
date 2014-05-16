from flask import Blueprint, request, render_template, redirect, url_for
from critiquebrainz.apis import musicbrainz

bp = Blueprint('search', __name__)

RESULTS_LIMIT = 10

@bp.route('/', endpoint='index')
def search_handler():
    query = request.args.get('query')
    type = request.args.get('type')
    offset = int(request.args.get('offset', default=0))
    if query:
        if type == "artist":
            count, results = musicbrainz.search_artists(query, limit=RESULTS_LIMIT, offset=offset)
        elif type == "release-group":
            count, results = musicbrainz.search_release_groups(query, limit=RESULTS_LIMIT, offset=offset)
        else:
            count, results = 0, []
    else:
        count, results = 0, []
    return render_template('search/index.html', query=query, type=type, results=results,
                           count=count, limit=RESULTS_LIMIT, offset=offset)


@bp.route('/selector', endpoint='selector')
def review_creation_selector_handler():
    artist = request.args.get('artist')
    release_group = request.args.get('release_group')
    next = request.args.get('next')
    if not next:
        return redirect(url_for('index'))
    offset = int(request.args.get('offset', default=0))
    if artist or release_group:
        count, results = musicbrainz.search_release_groups(artist=artist, release_group=release_group,
                                                          limit=RESULTS_LIMIT, offset=offset)
    else:
        count, results = 0, []
    return render_template('search/selector.html', next=next, artist=artist, release_group=release_group,
                           results=results, count=count, limit=RESULTS_LIMIT, offset=offset)
