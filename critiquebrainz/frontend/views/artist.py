from collections import OrderedDict
from flask import Blueprint, render_template, request, redirect, url_for
from flask_babel import gettext
from werkzeug.exceptions import BadRequest, NotFound
import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.musicbrainz_db.artist as mb_artist
import critiquebrainz.frontend.external.musicbrainz_db.release_group as mb_release_group
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions

artist_bp = Blueprint('artist', __name__)


@artist_bp.route('/<uuid:mbid>')
def entity(mbid):
    """Artist page.

    Displays release groups (split up into several sections depending on their
    type), artist information (type, members/member of, external links).
    """
    try:
        artist = mb_artist.get_artist_by_id(str(mbid))
    except mb_exceptions.NoDataFoundException:
        raise NotFound(gettext("Sorry, we couldn't find an artist with that MusicBrainz ID."))

    # Note that some artists might not have a list of members because they are not a band
    band_members = _get_band_members(artist)

    release_type = request.args.get('release_type', default='album')
    if release_type not in ['album', 'single', 'ep', 'broadcast', 'other']:  # supported release types
        raise BadRequest("Unsupported release type.")

    page = int(request.args.get('page', default=1))
    if page < 1:
        return redirect(url_for('.reviews'))
    limit = 20
    offset = (page - 1) * limit
    release_groups, count = mb_release_group.browse_release_groups(
        artist_id=artist['id'],
        release_types=[release_type],
        limit=limit,
        offset=offset,
    )
    for release_group in release_groups:
        # TODO(roman): Count reviews instead of fetching them.
        reviews, review_count = db_review.list_reviews(  # pylint: disable=unused-variable
            entity_id=release_group['id'],
            entity_type='release_group',
            sort='created', limit=1,
        )
        release_group['review_count'] = review_count

    return render_template(
        'artist/entity.html',
        id=artist['id'],
        artist=artist,
        release_type=release_type,
        release_groups=release_groups,
        page=page,
        limit=limit,
        count=count,
        band_members=band_members,
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
        artist_id = member.get('artist', {}).get('id', None)

        if artist_id in members_by_artist_id:
            members_by_artist_id[artist_id]['attributes'].extend(member.get('attribute-list', []))
        else:
            members_by_artist_id[artist_id] = {
                'name': member.get('artist', {}).get('name', ''),
                'periods': [],
                'attributes': member.get('attribute-list', []),
                'disambiguation': member.get('disambiguation', ''),
                'artist_id': member.get('artist', {}).get('id', None),
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
