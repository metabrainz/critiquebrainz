from flask import Blueprint, render_template, request, redirect, url_for
from flask_babel import gettext
from werkzeug.exceptions import BadRequest, NotFound
from critiquebrainz.frontend.external import musicbrainz
from critiquebrainz.data.model.review import Review
from collections import OrderedDict

artist_bp = Blueprint('artist', __name__)


@artist_bp.route('/<uuid:id>')
def entity(id):
    """Artist page.

    Displays release groups (split up into several sections depending on their
    type), artist information (type, members/member of, external links).
    """
    artist = musicbrainz.get_artist_by_id(id)
    if not artist:
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
    count, release_groups = musicbrainz.browse_release_groups(artist_id=id, release_types=[release_type],
                                                              limit=limit, offset=offset)
    for release_group in release_groups:
        # TODO(roman): Count reviews instead of fetching them.
        reviews, review_count = Review.list(entity_id=release_group['id'], entity_type='release_group', sort='created', limit=1)
        release_group['review_count'] = review_count

    return render_template(
        'artist/entity.html', id=id, artist=artist, release_type=release_type, release_groups=release_groups,
            page=page, limit=limit, count=count, band_members=band_members
    )


def _get_band_members(artist):
    band_members = artist.get('band-members', [])

    former_members = [member for member in band_members if member.get('ended', 'false') == 'true']
    current_members = [member for member in band_members if member.get('ended', 'false') == 'false']

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
    return members_by_artist_id.values()


def _get_period(member):
    begin_date = member.get('begin', None)
    end_date = member.get('end', None)

    def get_year_from_date(date):
        if date:
            return date.split('-')[0]
        else:
            return ''

    begin_date, end_date = get_year_from_date(begin_date), get_year_from_date(end_date)
    if begin_date or end_date:
        return begin_date, end_date
    else:
        return None
