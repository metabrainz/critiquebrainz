from flask import Blueprint, render_template, request
from werkzeug.exceptions import NotFound
from flask_login import current_user
from flask_babel import gettext
import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.musicbrainz_db.label as mb_label
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
from critiquebrainz.frontend.views import get_avg_rating, LABEL_REVIEWS_LIMIT
from critiquebrainz.frontend.forms.rate import RatingEditForm


label_bp = Blueprint('label', __name__)


@label_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    try:
        label = mb_label.get_label_by_id(id)
    except mb_exceptions.NoDataFoundException:
        raise NotFound(gettext("Sorry, we couldn't find a label with that MusicBrainz ID."))

    label_reviews_limit = LABEL_REVIEWS_LIMIT
    if request.args.get('reviews') == "all":
        label_reviews_limit = None

    if current_user.is_authenticated:
        my_reviews, my_count = db_review.list_reviews(
            entity_id=label['id'],
            entity_type='label',
            user_id=current_user.id,
        )
        my_review = my_reviews[0] if my_count else None
    else:
        my_review = None

    reviews_offset = 0
    reviews, reviews_count = db_review.list_reviews(
        entity_id=label['id'],
        entity_type='label',
        sort='popularity',
        limit=label_reviews_limit,
        offset=reviews_offset,
    )

    avg_rating = get_avg_rating(label['id'], "label")

    rating_form = RatingEditForm(entity_id=id, entity_type='label')
    rating_form.rating.data = my_review['rating'] if my_review else None

    return render_template(
        'label/entity.html',
        id=label['id'],
        label=label,
        reviews=reviews,
        reviews_limit=label_reviews_limit,
        reviews_count=reviews_count,
        avg_rating=avg_rating,
        rating_form=rating_form,
    )
