from collections import OrderedDict

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
from flask_babel import gettext
from werkzeug.exceptions import BadRequest, NotFound

import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.musicbrainz_db.artist as mb_artist
import critiquebrainz.frontend.external.musicbrainz_db.release_group as mb_release_group
from critiquebrainz.frontend.views import get_avg_rating, BROWSE_RELEASE_GROUPS_LIMIT, ARTIST_REVIEWS_LIMIT
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.external.bookbrainz_db import author as bb_author
from critiquebrainz.frontend.external.bookbrainz_db.common_entity import get_authors_for_artist

artist_bp = Blueprint('artist', __name__)


@artist_bp.route('/<uuid:id>')
def entity(id):
    """Artist page.

    Displays release groups (split up into several sections depending on their
    type), artist information (type, members/member of, external links).
    """
    artist = mb_artist.get_artist_by_mbid(str(id))
    if artist is None:
        raise NotFound(gettext("Sorry, we couldn't find an artist with that MusicBrainz ID."))

    author_bbids = get_authors_for_artist(id)
    author_info = {}
    if author_bbids:
        author_info = bb_author.fetch_multiple_authors(author_bbids)
        for author in author_info:
            reviews, count = db_review.list_reviews(
                entity_id=author,
                entity_type='bb_author',
                sort='popularity',
                limit=ARTIST_REVIEWS_LIMIT,
                offset=0,
            )
            author_info[author]['reviews'] = reviews
            author_info[author]['reviews_count'] = count

    author_info = author_info.values()

    # Note that some artists might not have a list of members because they are not a band
    band_members = _get_band_members(artist)

    artist_reviews_limit = ARTIST_REVIEWS_LIMIT
    if request.args.get('reviews') == "all":
        artist_reviews_limit = None

    my_review = None
    if current_user.is_authenticated:
        my_reviews, my_count = db_review.list_reviews(
            entity_id=artist['mbid'],
            entity_type='artist',
            user_id=current_user.id,
        )
        my_review = my_reviews[0] if my_count else None

    reviews_offset = 0
    reviews, reviews_count = db_review.list_reviews(
        entity_id=artist['mbid'],
        entity_type='artist',
        sort='popularity',
        limit=artist_reviews_limit,
        offset=reviews_offset,
    )

    avg_rating = get_avg_rating(artist['mbid'], "artist")

    rating_form = RatingEditForm(entity_id=id, entity_type='artist')
    rating_form.rating.data = my_review['rating'] if my_review else None

    release_type = request.args.get('release_type', default='album')
    if release_type not in ['album', 'single', 'ep', 'broadcast', 'other']:  # supported release types
        raise BadRequest("Unsupported release type.")

    try:
        page = int(request.args.get('page', default=1))
    except ValueError:
        raise BadRequest("Invalid page number!")
    
    if page < 1:
        return redirect(url_for('artist.entity', id=id))
    release_groups_offset = (page - 1) * BROWSE_RELEASE_GROUPS_LIMIT
    release_groups, release_group_count = mb_release_group.browse_release_groups(
        artist_id=artist['mbid'],
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

    return render_template(
        'artist/entity.html',
        id=artist['mbid'],
        artist=artist,
        release_type=release_type,
        release_groups=release_groups,
        page=page,
        author_info=author_info,
        reviews=reviews,
        reviews_limit=artist_reviews_limit,
        reviews_count=reviews_count,
        avg_rating=avg_rating,
        rating_form=rating_form,
        release_groups_limit=BROWSE_RELEASE_GROUPS_LIMIT,
        release_group_count=release_group_count,
        band_members=band_members,
        my_review=my_review,
    )


def _get_band_members(artist):
    band_members = artist.get('band-members', [])

    former_members = [member for member in band_members if member.get('ended', False) is True]
    current_members = [member for member in band_members if member.get('ended', False) is False]

    return {
        'former_members': _squash_duplicated_members(former_members),
        'current_members': _squash_duplicated_members(current_members)
    }


def _squash_duplicated_members(members):
    members_by_artist_id = OrderedDict()

    for member in members:
        artist_id = member.get('artist', {}).get('mbid', None)

        if artist_id in members_by_artist_id:
            members_by_artist_id[artist_id]['attributes'].extend(member.get('attribute-list', []))
        else:
            member_artist = member.get('artist', {})
            members_by_artist_id[artist_id] = {
                'name': member_artist.get('name', ''),
                'periods': [],
                'attributes': member.get('attribute-list', []),
                'comment': member_artist.get('comment', ''),
                'artist_id': member_artist.get('mbid', None),
                'ended': member.get('ended')
            }
        period = _get_period(member)
        if period:
            members_by_artist_id[artist_id]['periods'].append(period)
    return list(members_by_artist_id.values())


def _get_period(member):
    """Get period for which an artist is/was part of a group, orchestra or choir.

    Args:
        member (Dict): Dictionary containing the artist information.

    Returns:
        Tuple containing the begin and end year during which an artist was part of
        a group.
    """
    begin_date = member.get('begin-year', '')
    end_date = member.get('end-year', '')

    if not (begin_date or end_date):
        return None
    return str(begin_date), str(end_date)
