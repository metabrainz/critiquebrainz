from flask import Blueprint, render_template, request
from flask_login import current_user
from flask_babel import gettext
from werkzeug.exceptions import NotFound
import critiquebrainz.frontend.external.musicbrainz_db.place as mb_place
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.views import get_avg_rating
import critiquebrainz.db.review as db_review

place_bp = Blueprint('place', __name__)


@place_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    try:
        place = mb_place.get_place_by_id(id)
    except mb_exceptions.NoDataFoundException:
        raise NotFound(gettext("Sorry, we couldn't find a place with that MusicBrainz ID."))

    if current_user.is_authenticated:
        my_reviews, my_count = db_review.list_reviews(entity_id=place['id'],
            entity_type='place',
            user_id=current_user.id
        )
        my_review = my_reviews[0] if my_count else None
    else:
        my_review = None

    rating_form = RatingEditForm(entity_id=id, entity_type='place')
    rating_form.rating.data = my_review['rating'] if my_review else None

    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    reviews, count = db_review.list_reviews(
        entity_id=place['id'],
        entity_type='place',
        sort='popularity',
        limit=limit,
        offset=offset,
    )
    avg_rating = get_avg_rating(place['id'], "place")

    return render_template('place/entity.html', id=place['id'], place=place, reviews=reviews,
                           rating_form=rating_form, my_review=my_review, limit=limit, offset=offset,
                           count=count, avg_rating=avg_rating, current_user=current_user)
