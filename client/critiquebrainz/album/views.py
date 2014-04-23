from flask import Blueprint, render_template, request
from critiquebrainz.api import api
from critiquebrainz import musicbrainz


bp = Blueprint('album', __name__)


@bp.route('/<uuid:id>', endpoint='entity')
def release_group_entity_handler(id):
    album = musicbrainz.album_details(id)
    limit = int(request.args.get('limit', default=5))
    offset = int(request.args.get('offset', default=0))
    count, reviews = server.get_reviews(release_group=id, sort='created',
                                        limit=limit, offset=offset, inc=['user'])
    return render_template('album.html', id=id, album=album, reviews=reviews,
                           limit=limit, offset=offset, count=count)
