from flask import Blueprint, render_template
from werkzeug.exceptions import NotFound
from flask_babel import gettext
import critiquebrainz.frontend.external.musicbrainz_db.work as mb_work
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions

work_bp = Blueprint('work', __name__)


@work_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    try:
        work = mb_work.get_work_by_id(id)
    except mb_exceptions.NoDataFoundException:
        raise NotFound(gettext("Sorry, we couldn't find a work with that MusicBrainz ID."))

    return render_template('work/entity.html', id=work['id'], work=work)
