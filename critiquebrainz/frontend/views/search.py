from flask import Blueprint, request, render_template, redirect, jsonify, url_for
from critiquebrainz.frontend.external import musicbrainz
from critiquebrainz.data.model.user import User

search_bp = Blueprint('search', __name__)

RESULTS_LIMIT = 10


def search_users(query, limit=None, offset=None):
    users, count = User.list(display_name=query, limit=limit, offset=offset,
                             sort='name', is_blocked=False)
    return count, users


def search_wrapper(query, type, offset=None):
    search_types = {
        "artist": musicbrainz.search_artists,
        "event": musicbrainz.search_events,
        "release-group": musicbrainz.search_release_groups,
        "user": search_users,
    }
    if query and type in search_types:
        count, results = search_types[type](query, limit=RESULTS_LIMIT, offset=offset)
    else:
        count, results = 0, []
    return count, results


@search_bp.route('/')
def index():
    query = request.args.get('query')
    type = request.args.get('type')
    count, results = search_wrapper(query, type)
    return render_template('search/index.html', query=query, type=type, results=results, count=count, limit=RESULTS_LIMIT)


@search_bp.route('/more')
def more():
    query = request.args.get('query')
    type = request.args.get('type')
    page = int(request.args.get('page', default=0))
    offset = page * RESULTS_LIMIT
    count, results = search_wrapper(query, type, offset)
    template = render_template('search/results.html', type=type, results=results)
    return jsonify(results=template, more=(count-offset-RESULTS_LIMIT) > 0)


@search_bp.route('/selector')
def selector():
    artist = request.args.get('artist')
    release_group = request.args.get('release_group')
    event = request.args.get('event')
    type = request.args.get('type')
    next = request.args.get('next')
    if not next:
        return redirect(url_for('frontend.index'))
    if artist or release_group:
        count, results = musicbrainz.search_release_groups(artist=artist, release_group=release_group,
                                                           limit=RESULTS_LIMIT)
    elif event:
        count, results = musicbrainz.search_events(event, limit=RESULTS_LIMIT)
    else:
        count, results = 0, []
    return render_template('search/selector.html', next=next, type=type, results=results, count=count,
                           limit=RESULTS_LIMIT, artist=artist, release_group=release_group, event=event)


@search_bp.route('/selector/more')
def selector_more():
    artist = request.args.get('artist')
    release_group = request.args.get('release_group')
    event = request.args.get('event')
    type = request.args.get('type')
    page = int(request.args.get('page', default=0))
    offset = page * RESULTS_LIMIT
    if type == 'release-group':
        count, results = musicbrainz.search_release_groups(artist=artist, release_group=release_group,
                                                           limit=RESULTS_LIMIT, offset=offset)
    elif type == 'event':
        count, results = musicbrainz.search_events(event, limit=RESULTS_LIMIT, offset=offset)
    else:
        count, results = 0, []
    template = render_template('search/selector_results.html', results=results, type=type)
    return jsonify(results=template, more=(count-offset-RESULTS_LIMIT) > 0)
