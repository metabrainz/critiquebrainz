from flask import Blueprint, render_template, request, redirect, url_for
from flask_babel import gettext
from flask_login import current_user
from werkzeug.exceptions import NotFound, BadRequest

import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.musicbrainz_db.work as mb_work
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.views import get_avg_rating, WORK_REVIEWS_LIMIT, BROWSE_RECORDING_LIMIT
from critiquebrainz.frontend.external.bookbrainz_db.common_entity import get_literary_works_for_work
from critiquebrainz.frontend.external.bookbrainz_db import literary_work as bb_literary_work

work_bp = Blueprint('work', __name__)


@work_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    work = mb_work.get_work_by_mbid(id)
    if work is None:
        raise NotFound(gettext("Sorry, we couldn't find a work with that MusicBrainz ID."))

    literary_work_bbids = get_literary_works_for_work(id)
    literary_work_info = {}
    if literary_work_bbids:
        literary_work_info = bb_literary_work.fetch_multiple_literary_works(literary_work_bbids)
        for literary_work in literary_work_info:
            reviews, count = db_review.list_reviews(
                entity_id=literary_work,
                entity_type='bb_literary_work',
                sort='popularity',
                limit=WORK_REVIEWS_LIMIT,
                offset=0,
            )
            literary_work_info[literary_work]['reviews'] = reviews
            literary_work_info[literary_work]['reviews_count'] = count

    literary_work_info = literary_work_info.values()

    work_reviews_limit = WORK_REVIEWS_LIMIT
    if request.args.get('reviews') == "all":
        work_reviews_limit = None

    if current_user.is_authenticated:
        my_reviews, _ = db_review.list_reviews(
            entity_id=work['mbid'],
            entity_type='work',
            user_id=current_user.id,
        )
        my_review = my_reviews[0] if my_reviews else None
    else:
        my_review = None

    reviews_offset = 0
    reviews, reviews_count = db_review.list_reviews(
        entity_id=work['mbid'],
        entity_type='work',
        sort='popularity',
        limit=work_reviews_limit,
        offset=reviews_offset,
    )

    try:
        page = int(request.args.get('page', default=1))
    except ValueError:
        raise BadRequest("Invalid page number!")
    
    if page < 1:
        return redirect(url_for('work.entity', id=id))

    if 'recording-rels' in work:
        recording_rels = work['recording-rels']
    else:
        recording_rels = []

    recording_count = len(recording_rels)

    recording_offset = (page - 1) * BROWSE_RECORDING_LIMIT
    recording_rels = recording_rels[recording_offset:recording_offset + BROWSE_RECORDING_LIMIT]

    avg_rating = get_avg_rating(work['mbid'], "work")

    rating_form = RatingEditForm(entity_id=id, entity_type='work')
    rating_form.rating.data = my_review['rating'] if my_review else None

    return render_template('work/entity.html', id=work['mbid'], work=work, page=page, reviews=reviews,
                           literary_work_info=literary_work_info, my_review=my_review, reviews_limit=work_reviews_limit,
                           reviews_count=reviews_count, avg_rating=avg_rating, rating_form=rating_form,
                           recording_limit=BROWSE_RECORDING_LIMIT, recording_rels=recording_rels,
                           recording_count=recording_count, current_user=current_user)
