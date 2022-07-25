from flask import Blueprint, request, render_template, jsonify
from requests import HTTPError, JSONDecodeError, Timeout

from critiquebrainz.frontend.external import musicbrainz
from critiquebrainz.frontend.external import bookbrainz
from werkzeug.exceptions import BadRequest, ServiceUnavailable

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
        elif type == "work":
            count, results = musicbrainz.search_works(query, limit=RESULTS_LIMIT, offset=offset)
        elif type == "label":
            count, results = musicbrainz.search_labels(query, limit=RESULTS_LIMIT, offset=offset)
        elif type == "recording":
            count, results = musicbrainz.search_recordings(query, limit=RESULTS_LIMIT, offset=offset)
        elif type == "bb_edition_group":
            try:
                count, results = bookbrainz.search_edition_group(query, limit=RESULTS_LIMIT, offset=offset)
            except (HTTPError, JSONDecodeError, Timeout) :
                raise ServiceUnavailable('Request failed while searching for edition groups.')
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
    return render_template('search/index.html', query=query, type=type, results=results, count=count,
                           limit=RESULTS_LIMIT)


@search_bp.route('/more')
def more():
    query = request.args.get('query')
    type = request.args.get('type')
    try:
        page = int(request.args.get('page', default=0))
    except ValueError:
        raise BadRequest("Invalid page number!")

    offset = page * RESULTS_LIMIT
    count, results = search_wrapper(query, type, offset)
    template = render_template('search/results.html', type=type, results=results)
    return jsonify(results=template, more=(count - offset - RESULTS_LIMIT) > 0)
