from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from werkzeug.exceptions import NotFound, BadRequest
from flask_babel import gettext
import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.bookbrainz_db.series as bb_series
import critiquebrainz.frontend.external.bookbrainz_db.redirects as bb_redirects
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.views import get_avg_rating, SERIES_REVIEWS_LIMIT

bb_series_bp = Blueprint('bb_series', __name__)


@bb_series_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    series = bb_series.get_series_by_bbid(id)

    if not series:
        redirected_bbid = bb_redirects.get_redirected_bbid(id)
        if redirected_bbid:
            return redirect(url_for('bb_series.entity', id=redirected_bbid))

        raise NotFound(gettext("Sorry, we couldn't find a series with that BookBrainz ID."))

    try:
        reviews_limit = int(request.args.get('limit', default=SERIES_REVIEWS_LIMIT))
    except ValueError:
        raise BadRequest("Invalid limit parameter!")

    try:
        reviews_offset = int(request.args.get('offset', default=0))
    except ValueError:
        raise BadRequest("Invalid offset parameter!")

    if current_user.is_authenticated:
        my_reviews, _ = db_review.list_reviews(
            entity_id=series['bbid'],
            entity_type='bb_series',
            user_id=current_user.id,
        )
        my_review = my_reviews[0] if my_reviews else None
    else:
        my_review = None
    reviews, count = db_review.list_reviews(
        entity_id=series['bbid'],
        entity_type='bb_series',
        sort='popularity',
        limit=reviews_limit,
        offset=reviews_offset,
    )
    avg_rating = get_avg_rating(series['bbid'], "bb_series")

    rating_form = RatingEditForm(entity_id=id, entity_type='bb_series')
    rating_form.rating.data = my_review['rating'] if my_review else None

    rels_bbid = [rel['source_bbid'] for rel in series['rels']]
    series_rels_info = bb_series.fetch_series_rels_info(series['series_type'], rels_bbid)
    series_rels_info = series_rels_info.values()

    return render_template('bb_series/entity.html',
                           id=series['bbid'],
                           series=series,
                           series_rels_info=series_rels_info,
                           reviews=reviews,
                           my_review=my_review,
                           count=count,
                           rating_form=rating_form,
                           current_user=current_user,
                           limit=reviews_limit,
                           offset=reviews_offset,
                           avg_rating=avg_rating)
