from flask import Blueprint, request, render_template, redirect, jsonify, url_for
from critiquebrainz.apis import musicbrainz

search_bp = Blueprint('search', __name__)

RESULTS_LIMIT = 10


def search_wrapper(query, type, offset=None):
    if query:
        if type == "artist":
            count, results = musicbrainz.search_artists(query, limit=RESULTS_LIMIT, offset=offset)
        elif type == "release-group":
            count, results = musicbrainz.search_release_groups(query, limit=RESULTS_LIMIT, offset=offset)
        else:
            count, results = 0, []
    else:
        count, results = 0, []
    return count, results

@search_bp.route('/', endpoint='index')
def search_handler():
    query = request.args.get('query')
    type = request.args.get('type')
    count, results = search_wrapper(query, type)
    return render_template('search/index.html', query=query, type=type, results=results, count=count, limit=RESULTS_LIMIT)


@search_bp.route('/more', endpoint='more')
def more_handler():
    query = request.args.get('query')
    type = request.args.get('type')
    page = int(request.args.get('page', default=0))
    offset = page * RESULTS_LIMIT
    count, results = search_wrapper(query, type, offset)
    template = render_template('search/results.html', type=type, results=results)
    return jsonify(results=template, more=(count-offset-RESULTS_LIMIT) > 0)


@search_bp.route('/selector', endpoint='selector')
def review_creation_selector_handler():
    artist = request.args.get('artist')
    release_group = request.args.get('release_group')
    next = request.args.get('next')
    if not next:
        return redirect(url_for('index'))
    if artist or release_group:
        count, results = musicbrainz.search_release_groups(artist=artist, release_group=release_group,
                                                           limit=RESULTS_LIMIT)
    else:
        count, results = 0, []
    return render_template('search/selector.html', next=next, artist=artist, release_group=release_group,
                           results=results, count=count, limit=RESULTS_LIMIT)


@search_bp.route('/selector/more', endpoint='selector_more')
def selector_more_handler():
    artist = request.args.get('artist')
    release_group = request.args.get('release_group')
    page = int(request.args.get('page', default=0))
    offset = page * RESULTS_LIMIT
    if artist or release_group:
        count, results = musicbrainz.search_release_groups(artist=artist, release_group=release_group,
                                                           limit=RESULTS_LIMIT, offset=offset)
    else:
        count, results = 0, []
    template = render_template('search/selector_results.html', results=results)
    return jsonify(results=template, more=(count-offset-RESULTS_LIMIT) > 0)
