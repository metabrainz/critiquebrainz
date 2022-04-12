from flask import Blueprint, render_template, request, redirect, url_for
from flask_babel import gettext
from flask_login import current_user
from werkzeug.exceptions import BadRequest, NotFound

import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.musicbrainz_db.label as mb_label
import critiquebrainz.frontend.external.musicbrainz_db.release_group as mb_release_group
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.views import get_avg_rating, LABEL_REVIEWS_LIMIT, BROWSE_RELEASE_GROUPS_LIMIT

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

    release_type = request.args.get('release_type', default='album')
    if release_type not in ['album', 'single', 'ep', 'broadcast', 'other']:  # supported release types
        raise BadRequest("Unsupported release type.")

    try:
        page = int(request.args.get('page', default=1))
    except ValueError:
        raise BadRequest("Invalid page number!")

    if page < 1:
        return redirect(url_for('label.entity', id=id))
    release_groups_offset = (page - 1) * BROWSE_RELEASE_GROUPS_LIMIT
    release_groups, release_group_count = mb_release_group.get_release_groups_for_label(
        label_id=label['mbid'],
        release_types=[release_type],
        limit=BROWSE_RELEASE_GROUPS_LIMIT,
        offset=release_groups_offset,
    )
    for release_group in release_groups:
        # TODO(roman): Count reviews instead of fetching them.
        _, release_group_review_count = db_review.list_reviews(  # pylint: disable=unused-variable
            entity_id=release_group['mbid'],
            entity_type='release_group',
            sort='published_on', limit=1,
        )
        release_group['review_count'] = release_group_review_count

    return render_template('label/entity.html', id=label['mbid'], label=label, release_type=release_type, 
                           release_groups=release_groups, page=page, reviews=reviews, my_review=my_review,
                           reviews_limit=label_reviews_limit, reviews_count=reviews_count, avg_rating=avg_rating,
                           rating_form=rating_form, release_groups_limit=BROWSE_RELEASE_GROUPS_LIMIT,
                           release_group_count=release_group_count, current_user=current_user)
