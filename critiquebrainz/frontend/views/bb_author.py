from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from werkzeug.exceptions import NotFound, BadRequest
from flask_babel import gettext
import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.bookbrainz_db.author as bb_author
import critiquebrainz.frontend.external.bookbrainz_db.literary_work as bb_literary_work
import critiquebrainz.frontend.external.bookbrainz_db.redirects as bb_redirects
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.views import get_avg_rating, AUTHOR_REVIEWS_LIMIT
from brainzutils.musicbrainz_db.artist import fetch_multiple_artists

bb_author_bp = Blueprint('bb_author', __name__)

LITERARY_WORK_TYPE_NOVEL = 'Novel'
LITERARY_WORK_TYPE_SHORT_STORY = 'Short Story'
LITERARY_WORK_TYPE_POEM = 'Poem'
LITERARY_WORK_TYPE_OTHER = 'other'
VALID_LITERARY_WORK_PARAMS = [LITERARY_WORK_TYPE_NOVEL, LITERARY_WORK_TYPE_SHORT_STORY, LITERARY_WORK_TYPE_POEM, LITERARY_WORK_TYPE_OTHER]


@bb_author_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    author = bb_author.get_author_by_bbid(id)

    if not author:
        redirected_bbid = bb_redirects.get_redirected_bbid(id)
        if redirected_bbid:
            return redirect(url_for('bb_author.entity', id=redirected_bbid))
        raise NotFound(gettext("Sorry, we couldn't find an author with that BookBrainz ID."))

    artist_info = {}
    if author['identifiers']:
        mb_artist_mbid = []
        for identifier in author['identifiers']:
            if identifier['name'] == 'MusicBrainz Artist ID':
                mb_artist_mbid.append(identifier['value'])

        if mb_artist_mbid:
            artist_info = fetch_multiple_artists(mb_artist_mbid)
            for artist in artist_info:
                reviews, count = db_review.list_reviews(
                    entity_id=artist,
                    entity_type='artist',
                    sort='popularity',
                    limit=AUTHOR_REVIEWS_LIMIT,
                    offset=0,
                )
                artist_info[artist]['reviews'] = reviews
                artist_info[artist]['reviews_count'] = count

    artist_info = artist_info.values()

    literary_work_type = request.args.get('literary_work_type')
    if not literary_work_type:
        literary_work_type = LITERARY_WORK_TYPE_NOVEL

    if literary_work_type not in VALID_LITERARY_WORK_PARAMS:  # supported literary_work types
        raise BadRequest("Unsupported literary_work type.")

    if author['rels']:
        literary_work_bbid = [rel['target_bbid'] for rel in author['rels']]
    else:
        literary_work_bbid = []
    literary_works = bb_literary_work.fetch_multiple_literary_works(literary_work_bbid, literary_work_type)


    try:
        reviews_limit = int(request.args.get('limit', default=AUTHOR_REVIEWS_LIMIT))
    except ValueError:
        raise BadRequest("Invalid limit parameter!")

    try:
        reviews_offset = int(request.args.get('offset', default=0))
    except ValueError:
        raise BadRequest("Invalid offset parameter!")

    if current_user.is_authenticated:
        my_reviews, _ = db_review.list_reviews(
            entity_id=author['bbid'],
            entity_type='bb_author',
            user_id=current_user.id,
        )
        my_review = my_reviews[0] if my_reviews else None
    else:
        my_review = None

    reviews, count = db_review.list_reviews(
        entity_id=author['bbid'],
        entity_type='bb_author',
        sort='popularity',
        limit=reviews_limit,
        offset=reviews_offset,
    )
    avg_rating = get_avg_rating(author['bbid'], "bb_author")

    rating_form = RatingEditForm(entity_id=id, entity_type='bb_author')
    rating_form.rating.data = my_review['rating'] if my_review else None

    if author['begin_day'] and author['begin_month'] and author['begin_year']:
        begin_date = datetime(author['begin_year'], author['begin_month'], author['begin_day'])
    else:
        begin_date = None

    if author['end_day'] and author['end_month'] and author['end_year']:
        end_date = datetime(author['end_year'], author['end_month'], author['end_day'])
    else:
        end_date = None

    begin_area = None
    end_area = None
    for area in author['area_info']:
        if author['begin_area_id'] and author['begin_area_id'] == area['id']:
            begin_area = area
        if author['end_area_id'] and author['end_area_id'] == area['id']:
            end_area = area

    return render_template('bb_author/entity.html',
                           id=author['bbid'],
                           author=author,
                           literary_works=literary_works,
                           literary_work_type=literary_work_type,
                           begin_date=begin_date,
                           end_date=end_date,
                           begin_area=begin_area,
                           end_area=end_area,
                           artist_info=artist_info,
                           reviews=reviews,
                           my_review=my_review,
                           count=count,
                           rating_form=rating_form,
                           current_user=current_user,
                           limit=reviews_limit,
                           offset=reviews_offset,
                           avg_rating=avg_rating)
