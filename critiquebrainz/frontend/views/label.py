from flask import Blueprint, render_template, request
from flask_babel import gettext
from flask_login import current_user
from werkzeug.exceptions import NotFound

import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.musicbrainz_db.label as mb_label
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.views import get_avg_rating, LABEL_REVIEWS_LIMIT

label_bp = Blueprint('label', __name__)


@label_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    label = mb_label.get_label_by_mbid(id)
    if label is None:
        raise NotFound(gettext("Sorry, we couldn't find a label with that MusicBrainz ID."))

    label_reviews_limit = LABEL_REVIEWS_LIMIT
    if request.args.get('reviews') == "all":
        label_reviews_limit = None

    if current_user.is_authenticated:
        my_reviews, _ = db_review.list_reviews(
            entity_id=label['mbid'],
            entity_type='label',
            user_id=current_user.id,
        )
        my_review = my_reviews[0] if my_reviews else None
    else:
        my_review = None

    reviews_offset = 0
    reviews, reviews_count = db_review.list_reviews(
        entity_id=label['mbid'],
        entity_type='label',
        sort='popularity',
        limit=label_reviews_limit,
        offset=reviews_offset,
    )

    avg_rating = get_avg_rating(label['mbid'], "label")

    rating_form = RatingEditForm(entity_id=id, entity_type='label')
    rating_form.rating.data = my_review['rating'] if my_review else None

    return render_template('label/entity.html', id=label['mbid'], label=label,
                           reviews=reviews, my_review=my_review, reviews_limit=label_reviews_limit,
                           reviews_count=reviews_count, avg_rating=avg_rating, rating_form=rating_form,
                           current_user=current_user)
