from flask import Blueprint, render_template
from flask_babel import gettext
from critiquebrainz.frontend.apis import musicbrainz
from werkzeug.exceptions import NotFound


event_bp = Blueprint('event', __name__)


@event_bp.route('/<uuid:id>')
def entity(id):
    event = musicbrainz.get_event_by_id(id)
    if not event:
        raise NotFound(gettext("Sorry, we couldn't find a event with that MusicBrainz ID."))

    reviews = []
    return render_template('event.html', id=id, event=event, reviews=reviews)
