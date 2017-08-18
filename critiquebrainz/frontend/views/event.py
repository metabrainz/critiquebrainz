from itertools import groupby
from operator import itemgetter
from flask import Blueprint, render_template, request
from flask_login import current_user
from flask_babel import gettext
from werkzeug.exceptions import NotFound
<<<<<<< HEAD
import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.musicbrainz_db.event as mb_event
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
=======
import critiquebrainz.db.avg_rating as db_avg_rating
import critiquebrainz.db.exceptions as db_exceptions
>>>>>>> 5004587... Display average rating on entity page


event_bp = Blueprint('event', __name__)


@event_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    try:
        event = mb_event.get_event_by_id(id)
    except mb_exceptions.NoDataFoundException:
        raise NotFound(gettext("Sorry, we couldn't find a event with that MusicBrainz ID."))

    if 'artist-rels' in event and event['artist-rels']:
        artists_sorted = sorted(event['artist-rels'], key=itemgetter('type'))
        event['artists_grouped'] = groupby(artists_sorted, itemgetter('type'))

    if current_user.is_authenticated:
        my_reviews, my_count = db_review.list_reviews(entity_id=event['id'], entity_type='event', user_id=current_user.id)
        if my_count != 0:
            my_review = my_reviews[0]
        else:
            my_review = None
    else:
        my_review = None

    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    reviews, count = db_review.list_reviews(entity_id=id, entity_type='event', sort='popularity', limit=limit, offset=offset)
    try:
        avg_rating = db_avg_rating.get(event['id'], "event")
        avg_rating["rating"] = round(avg_rating["rating"] / 20, 1)
    except db_exceptions.NoDataFoundException:
        avg_rating = None

    return render_template('event/entity.html', id=event['id'], event=event, reviews=reviews,
                           my_review=my_review, limit=limit, offset=offset, count=count, avg_rating=avg_rating)
