from flask import Blueprint, request, render_template
from critiquebrainz import app
from critiquebrainz.api import api
from critiquebrainz.exceptions import APIError
from critiquebrainz.musicbrainz import musicbrainz

bp = Blueprint('search', __name__)

@bp.route('/', endpoint='release_group')
def release_group_handler():
    artist = request.args.get('artist')
    album = request.args.get('album')
    next = request.args.get('next')
    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    if artist or album:
        results = musicbrainz.search_release_group(artist, album, limit, offset)
    else:
        results = []
    return render_template('search.html', results=results, next=next)
