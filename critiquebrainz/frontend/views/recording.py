from flask import Blueprint, render_template
from werkzeug.exceptions import NotFound
from flask_babel import gettext
import critiquebrainz.frontend.external.musicbrainz_db.recording as mb_recording
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions

recording_bp = Blueprint('recording', __name__)


@recording_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    try:
        recording = mb_recording.get_recording_by_id(id)
    except mb_exceptions.NoDataFoundException:
        raise NotFound(gettext("Sorry, we couldn't find a recording with that MusicBrainz ID."))

    return render_template('recording/entity.html', id=recording['id'], recording=recording)
