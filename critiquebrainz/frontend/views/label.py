from flask import Blueprint, render_template
from werkzeug.exceptions import NotFound
from flask_babel import gettext
import critiquebrainz.frontend.external.musicbrainz_db.label as mb_label
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions

label_bp = Blueprint('label', __name__)


@label_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    try:
        label = mb_label.get_label_by_id(id)
    except mb_exceptions.NoDataFoundException:
        raise NotFound(gettext("Sorry, we couldn't find a label with that MusicBrainz ID."))

    return render_template('label/entity.html', id=label['id'], label=label)
