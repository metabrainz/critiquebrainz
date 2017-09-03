from flask import Blueprint, render_template, request
from flask_login import current_user
from flask_babel import gettext
import critiquebrainz.frontend.external.musicbrainz_db.place as mb_place
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
import critiquebrainz.db.review as db_review
from werkzeug.exceptions import NotFound
import critiquebrainz.db.avg_rating as db_avg_rating
import critiquebrainz.db.exceptions as db_exceptions

place_bp = Blueprint('place', __name__)


@place_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    try:
        place = mb_place.get_place_by_id(id)
    except mb_exceptions.NoDataFoundException:
        raise NotFound(gettext("Sorry, we couldn't find a place with that MusicBrainz ID."))

    if current_user.is_authenticated:
        my_reviews, my_count = db_review.list_reviews(entity_id=place['id'], entity_type='place', user_id=current_user.id)
        if my_count != 0:
            my_review = my_reviews[0]
        else:
            my_review = None
    else:
        my_review = None

    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    reviews, count = db_review.list_reviews(
        entity_id=place['id'],
        entity_type='place',
        sort='popularity',
        limit=limit,
        offset=offset,
    )
    try:
        avg_rating = db_avg_rating.get(id, "place")
        avg_rating["rating"] = round(avg_rating["rating"] / 20, 1)
    except db_exceptions.NoDataFoundException:
        avg_rating = None

    return render_template('place/entity.html', id=id, place=place, reviews=reviews,
                           my_review=my_review, limit=limit, offset=offset, count=count, avg_rating=avg_rating)
