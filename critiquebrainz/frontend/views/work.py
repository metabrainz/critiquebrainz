from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.exceptions import NotFound
from flask_login import current_user
from flask_babel import gettext
import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.musicbrainz_db.work as mb_work
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
from critiquebrainz.frontend.views import get_avg_rating, WORK_REVIEWS_LIMIT, BROWSE_RECORDING_LIMIT
from critiquebrainz.frontend.forms.rate import RatingEditForm


work_bp = Blueprint('work', __name__)


@work_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    try:
        work = mb_work.get_work_by_id(id)
    except mb_exceptions.NoDataFoundException:
        raise NotFound(gettext("Sorry, we couldn't find a work with that MusicBrainz ID."))

    work_reviews_limit = WORK_REVIEWS_LIMIT
    if request.args.get('reviews') == "all":
        work_reviews_limit = None

    if current_user.is_authenticated:
        my_reviews, my_count = db_review.list_reviews(
            entity_id=work['id'],
            entity_type='work',
            user_id=current_user.id,
        )
        my_review = my_reviews[0] if my_count else None
    else:
        my_review = None

    reviews_offset = 0
    reviews, reviews_count = db_review.list_reviews(
        entity_id=work['id'],
        entity_type='work',
        sort='popularity',
        limit=work_reviews_limit,
        offset=reviews_offset,
    )

    page = int(request.args.get('page', default=1))
    if page < 1:
        return redirect(url_for('.reviews'))

    recording_rels = work['recording-rels']
    recording_count = len(recording_rels)

    recording_offset = (page - 1) * BROWSE_RECORDING_LIMIT
    recording_rels = recording_rels[recording_offset:recording_offset + BROWSE_RECORDING_LIMIT]

    avg_rating = get_avg_rating(work['id'], "work")

    rating_form = RatingEditForm(entity_id=id, entity_type='work')
    rating_form.rating.data = my_review['rating'] if my_review else None

    return render_template('work/entity.html', id=work['id'], work=work, page=page,
                           reviews=reviews, my_review=my_review, reviews_limit=work_reviews_limit,
                           reviews_count=reviews_count, avg_rating=avg_rating, rating_form=rating_form,
                           recording_limit=BROWSE_RECORDING_LIMIT, recording_rels=recording_rels,
                           recording_count=recording_count, current_user=current_user)
