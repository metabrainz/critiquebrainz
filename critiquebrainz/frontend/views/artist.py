from flask import Blueprint, render_template, request, redirect, url_for
from flask_babel import gettext
from werkzeug.exceptions import BadRequest, NotFound
from critiquebrainz.frontend.external import musicbrainz
from critiquebrainz.data.model.review import Review

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

    # Preparing artist-rels
    if 'band-members' in artist:
        artist['current_members'] = []
        artist['former_members'] = []
        for member in artist['band-members']:
            if 'ended' in member and member['ended'] == 'true':
                artist['former_members'].append(member)
            else:
                artist['current_members'].append(member)

        squash_duplicated_members(artist['former_members'])
        squash_duplicated_members(artist['current_members'])

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
    return render_template('artist.html', id=id, artist=artist, release_type=release_type,
                           release_groups=release_groups, page=page, limit=limit, count=count)


def squash_duplicated_members(members):
    target_order = []
    for member in members:
        if member['target'] not in target_order:
            target_order.append(member['target'])

    members_by_target = {}

    for member in members:
        target = member['target']
        if target in members_by_target:
            target_member = members_by_target[target]
            target_member['attribute-list'].extend(member.get('attribute-list', []))

            period = _get_period(member)
            if period:
                target_member['periods'].append(period)
        else:
            members_by_target[target] = member

            if not member.get('attribute-list', None):
                member['attribute-list'] = []

            member['periods'] = []
            period = _get_period(member)
            if period:
                member['periods'].append(period)

    for target in members_by_target:
        members_by_target[target]['periods'].sort(key=lambda x: x[1])

    del members[:]
    members.extend([members_by_target[target] for target in target_order])


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
