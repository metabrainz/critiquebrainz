from flask import Blueprint, request, render_template, redirect, jsonify, url_for
from critiquebrainz.frontend.external import musicbrainz

search_bp = Blueprint('search', __name__)

RESULTS_LIMIT = 10


def search_wrapper(query, type, offset=None):
    if query:
        if type == "artist":
            count, results = musicbrainz.search_artists(query, limit=RESULTS_LIMIT, offset=offset)
        elif type == "event":
            count, results = musicbrainz.search_events(query, limit=RESULTS_LIMIT, offset=offset)
        elif type == "place":
            count, results = musicbrainz.search_places(query, limit=RESULTS_LIMIT, offset=offset)
        elif type == "release-group":
            count, results = musicbrainz.search_release_groups(query, limit=RESULTS_LIMIT, offset=offset)
        elif type == "recording":
            count, results = musicbrainz.search_recordings(query, limit=RESULTS_LIMIT, offset=offset)
        elif type == "label":
            count, results = musicbrainz.search_labels(query, limit=RESULTS_LIMIT, offset=offset)
        elif type == "work":
            count, results = musicbrainz.search_works(query, limit=RESULTS_LIMIT, offset=offset)
        else:
            count, results = 0, []
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
    return jsonify(results=template, more=(count - offset - RESULTS_LIMIT) > 0)


@search_bp.route('/selector')
def selector():
    release_group = request.args.get('release_group')
    recording = request.args.get('recording')
    artist = request.args.get('artist')
    label = request.args.get('label')
    event = request.args.get('event')
    place = request.args.get('place')
    work = request.args.get('work')
    type = request.args.get('type')
    next = request.args.get('next')
    if not next:
        return redirect(url_for('frontend.index'))
    if release_group:
        count, results = musicbrainz.search_release_groups(release_group, limit=RESULTS_LIMIT)
    elif recording:
        count, results = musicbrainz.search_recordings(recording, limit=RESULTS_LIMIT)
    elif artist:
        count, results = musicbrainz.search_artists(artist, limit=RESULTS_LIMIT)
    elif label:
        count, results = musicbrainz.search_labels(label, limit=RESULTS_LIMIT)
    elif work:
        count, results = musicbrainz.search_works(work, limit=RESULTS_LIMIT)
    elif event:
        count, results = musicbrainz.search_events(event, limit=RESULTS_LIMIT)
    elif place:
        count, results = musicbrainz.search_places(place, limit=RESULTS_LIMIT)
    else:
        count, results = 0, []
    return render_template('search/selector.html', next=next, type=type,
                           results=results, count=count, limit=RESULTS_LIMIT,
                           artist=artist, release_group=release_group, event=event,
                           recording=recording, work=work, label=label,
                           place=place)


@search_bp.route('/selector/more')
def selector_more():
    artist = request.args.get('artist')
    recording = request.args.get('recording')
    release_group = request.args.get('release_group')
    label = request.args.get('label')
    event = request.args.get('event')
    place = request.args.get('place')
    work = request.args.get('work')
    type = request.args.get('type')
    page = int(request.args.get('page', default=0))
    offset = page * RESULTS_LIMIT
    if type == 'release-group':
        count, results = musicbrainz.search_release_groups(release_group,
                                                           limit=RESULTS_LIMIT, offset=offset)
    elif type == 'recording':
        count, results = musicbrainz.search_recordings(recording, limit=RESULTS_LIMIT, offset=offset)
    elif type == 'artist':
        count, results = musicbrainz.search_artists(artist, limit=RESULTS_LIMIT, offset=offset)
    elif type == 'label':
        count, results = musicbrainz.search_labels(label, limit=RESULTS_LIMIT, offset=offset)
    elif type == 'work':
        count, results = musicbrainz.search_works(work, limit=RESULTS_LIMIT, offset=offset)
    elif type == 'event':
        count, results = musicbrainz.search_events(event, limit=RESULTS_LIMIT, offset=offset)
    elif type == 'place':
        count, results = musicbrainz.search_places(place, limit=RESULTS_LIMIT, offset=offset)
    else:
        count, results = 0, []
    template = render_template('search/selector_results.html', results=results, type=type)
    return jsonify(results=template, more=(count - offset - RESULTS_LIMIT) > 0)
