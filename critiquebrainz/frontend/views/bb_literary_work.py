from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from werkzeug.exceptions import NotFound, BadRequest
from flask_babel import gettext
import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.bookbrainz_db.literary_work as bb_literary_work
import critiquebrainz.frontend.external.bookbrainz_db.edition_group as bb_edition_group
import critiquebrainz.frontend.external.bookbrainz_db.redirects as bb_redirects
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.views import get_avg_rating, LITERARY_WORK_REVIEWS_LIMIT, BROWSE_LITERARY_WORK_LIMIT

bb_literary_work_bp = Blueprint('bb_literary_work', __name__)


@bb_literary_work_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    literary_work = bb_literary_work.get_literary_work_by_bbid(id)

    if not literary_work:
        redirected_bbid = bb_redirects.get_redirected_bbid(id)
        if redirected_bbid:
            return redirect(url_for('bb_literary_work.entity', id=redirected_bbid))

        raise NotFound(gettext("Sorry, we couldn't find a work with that BookBrainz ID."))

    try:
        reviews_limit = int(request.args.get('limit', default=LITERARY_WORK_REVIEWS_LIMIT))
    except ValueError:
        raise BadRequest("Invalid limit parameter!")

    try:
        reviews_offset = int(request.args.get('offset', default=0))
    except ValueError:
        raise BadRequest("Invalid offset parameter!")

    if current_user.is_authenticated:
        my_reviews, _ = db_review.list_reviews(
            entity_id=literary_work['bbid'],
            entity_type='bb_literary_work',
            user_id=current_user.id,
        )
        my_review = my_reviews[0] if my_reviews else None
    else:
        my_review = None
    reviews, count = db_review.list_reviews(
        entity_id=literary_work['bbid'],
        entity_type='bb_literary_work',
        sort='popularity',
        limit=reviews_limit,
        offset=reviews_offset,
    )
    avg_rating = get_avg_rating(literary_work['bbid'], "bb_literary_work")

    rating_form = RatingEditForm(entity_id=id, entity_type='bb_literary_work')
    rating_form.rating.data = my_review['rating'] if my_review else None

    page = request.args.get('page')
    if page:
        try:
            page = int(page)
        except ValueError:
            raise BadRequest("Invalid page number!")
    else:
        page = 1

    if page < 1:
        return redirect(url_for('bb_literary_work.entity', id=id))

    if literary_work['rels']:
        work_rels_bbid = [rel['source_bbid'] for rel in literary_work['rels']]
        work_rels_count = len(work_rels_bbid)
        work_rels_info = bb_literary_work.fetch_multiple_literary_works(
            bbids=work_rels_bbid,
            limit=BROWSE_LITERARY_WORK_LIMIT,
            offset=(page - 1) * BROWSE_LITERARY_WORK_LIMIT
        ).values()
    else:
        work_rels_bbid = []
        work_rels_count = 0
        work_rels_info = []

    edition_group_bbids = bb_literary_work.fetch_edition_groups_for_works(id)
    edition_groups_info = bb_edition_group.fetch_multiple_edition_groups(edition_group_bbids).values()

    return render_template('bb_literary_work/entity.html',
                           id=literary_work['bbid'],
                           literary_work=literary_work,
                           translation_rels_works=work_rels_info,
                           work_rels_count=work_rels_count,
                           work_rels_limit=BROWSE_LITERARY_WORK_LIMIT,
                           edition_groups_info=edition_groups_info,
                           page=page,
                           reviews=reviews,
                           my_review=my_review,
                           count=count,
                           rating_form=rating_form,
                           current_user=current_user,
                           limit=reviews_limit,
                           offset=reviews_offset,
                           avg_rating=avg_rating)
