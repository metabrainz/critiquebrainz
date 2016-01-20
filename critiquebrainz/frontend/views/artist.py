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

        artist['former_members'] = squash_members_attributes(artist['former_members'])
        artist['current_members'] = squash_members_attributes(artist['current_members'])

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


def squash_members_attributes(members):
    members = [member.copy() for member in members]
    ids_order = dict([(member['target'], index) for index, member in enumerate(members)])
    
    members.sort(key=lambda x: x['target'])
    result_members = []

    for i in range(0, len(members)):
        if i == 0 or members[i]['target'] != members[i-1]['target']:
            if not members[i].get('attribute-list', None):
                members[i]['attribute-list'] = []
            members[i]['periods'] = []
            period = get_period(members[i])
            if period:
                members[i]['periods'].append(period)
            j = i+1
            while j < len(members) and members[j]['target'] == members[i]['target']:
                members[i]['attribute-list'].extend(members[j].get('attribute-list', []))
                period = get_period(members[i])
                if(period):
                    members[i]['periods'].append(period)
                j += 1
            result_members.append(members[i])
            members[i]['periods'].sort(key=lambda x: x[1], reverse=True)

    result_members.sort(key=lambda x: ids_order[x['target']])
    return result_members


def get_period(member):
    begin_date = member.get('begin', None)
    end_date = member.get('end', None)
    begin_date, end_date = get_year_from_date(begin_date), get_year_from_date(end_date)

    if begin_date or end_date:
        return (begin_date, end_date)
    else:
        return None


def get_year_from_date(date):
    if date:
        return date.split('-')[0]
    else:
        return ''
