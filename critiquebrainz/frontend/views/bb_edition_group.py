from flask import Blueprint, render_template, request
from flask_login import current_user
from werkzeug.exceptions import NotFound, BadRequest
from flask_babel import gettext
import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.bookbrainz_db.edition_group as bb_edition_group
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.views import get_avg_rating, EDITION_GROUP_REVIEWS_LIMIT


edition_group_bp = Blueprint('edition_group', __name__)


@edition_group_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    edition_group = bb_edition_group.get_edition_group_by_bbid(id)

    if edition_group is None:
        raise NotFound(gettext("Sorry, we couldn't find an edition group with that BookBrainz ID."))

    try:
        reviews_limit = int(request.args.get('limit', default=EDITION_GROUP_REVIEWS_LIMIT))
    except ValueError:
        raise BadRequest("Invalid limit parameter!")

    try:
        reviews_offset = int(request.args.get('offset', default=0))
    except ValueError:
        raise BadRequest("Invalid offset parameter!")

    if current_user.is_authenticated:
        my_reviews, _ = db_review.list_reviews(
            entity_id=edition_group['bbid'],
            entity_type='bb_edition_group',
            user_id=current_user.id,
        )
        my_review = my_reviews[0] if my_reviews else None
    else:
        my_review = None
    reviews, count = db_review.list_reviews(
        entity_id=edition_group['bbid'],
        entity_type='bb_edition_group',
        sort='popularity',
        limit=reviews_limit,
        offset=reviews_offset,
    )
    avg_rating = get_avg_rating(edition_group['bbid'], "bb_edition_group")

    rating_form = RatingEditForm(entity_id=id, entity_type='bb_edition_group')
    rating_form.rating.data = my_review['rating'] if my_review else None

    return render_template('bb_edition_group/entity.html',
                           id=edition_group['bbid'],
                           edition_group=edition_group,
                           reviews=reviews,
                           my_review=my_review,
                           count=count,
                           rating_form=rating_form,
                           current_user=current_user,
                           limit=reviews_limit,
                           offset=reviews_offset,
                           avg_rating=avg_rating)
