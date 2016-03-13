from itertools import groupby
from operator import itemgetter
from flask import Blueprint, render_template, request
from flask_login import current_user
from flask_babel import gettext
from critiquebrainz.frontend.external import musicbrainz
from critiquebrainz.data.model.review import Review
from werkzeug.exceptions import NotFound


event_bp = Blueprint('event', __name__)


@event_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    event = musicbrainz.get_event_by_id(id)
    if not event:
        raise NotFound(gettext("Sorry, we couldn't find a event with that MusicBrainz ID."))

    if 'artist-relation-list' in event and event['artist-relation-list']:
        artists_sorted = sorted(event['artist-relation-list'], key=itemgetter('type'))
        event['artists_grouped'] = groupby(artists_sorted, itemgetter('type'))

    if current_user.is_authenticated():
        my_reviews, my_count = Review.list(entity_id=id, entity_type='event', user_id=current_user.id)
        if my_count != 0:
            my_review = my_reviews[0]
        else:
            my_review = None
    else:
        my_review = None

    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    reviews, count = Review.list(entity_id=id, entity_type='event', sort='rating', limit=limit, offset=offset)

    return render_template('event/entity.html', id=id, event=event, reviews=reviews,
                           my_review=my_review, limit=limit, offset=offset, count=count)
