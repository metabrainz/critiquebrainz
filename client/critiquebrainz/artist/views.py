from flask import Blueprint, render_template
from critiquebrainz import musicbrainz


bp = Blueprint('artist', __name__)


@bp.route('/<uuid:id>', endpoint='entity')
def artist_entity_handler(id):
    artist = musicbrainz.artist_details(id)
    return render_template('artist.html', id=id, artist=artist)
