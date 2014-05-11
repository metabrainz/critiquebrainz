from flask import Blueprint, request, render_template, redirect, url_for
from critiquebrainz.musicbrainz import musicbrainz

bp = Blueprint('search', __name__)


@bp.route('/', endpoint='index')
def search_handler():
    query = request.args.get('query')
    type = request.args.get('type')
    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    if query:
        if type == "artist":
            results = musicbrainz.search_artist(query, limit=limit, offset=offset)
        elif type == "release-group":
            results = musicbrainz.search_release_group(query, limit=limit, offset=offset)
        else:
            results = []
    else:
        results = []
    return render_template('search/index.html', results=results, type=type)


@bp.route('/selector', endpoint='selector')
def review_creation_selector_handler():
    artist = request.args.get('artist')
    release_group = request.args.get('release_group')
    next = request.args.get('next')
    if not next:
        return redirect(url_for('index'))
    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    if artist or release_group:
        results = musicbrainz.search_release_group(artist=artist, release_group=release_group,
                                                   limit=limit, offset=offset)
    else:
        results = []
    return render_template('search/selector.html', results=results, next=next)
