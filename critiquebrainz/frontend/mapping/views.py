from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required, current_user
from flask_babel import gettext
from werkzeug.exceptions import NotFound
import critiquebrainz.frontend.apis.spotify as spotify_api
from critiquebrainz.frontend.apis import musicbrainz, mbspotify
from urlparse import urlparse
import os.path
import string

mapping_bp = Blueprint('mapping', __name__)


@mapping_bp.route('/<uuid:release_group_id>')
def spotify_list(release_group_id):
    """This view lists all Spotify albums mapped to a specified release group."""
    spotify_mappings = mbspotify.mappings(str(release_group_id))

    # Converting Spotify URIs to IDs
    spotify_ids = []
    for mapping in spotify_mappings:
        spotify_ids.append(mapping[14:])

    if len(spotify_ids) > 0:
        spotify_albums = spotify_api.get_multiple_albums(spotify_ids)
    else:
        spotify_albums = []
    release_group = musicbrainz.get_release_group_by_id(release_group_id)
    if not release_group:
        raise NotFound("Can't find release group with a specified ID.")
    return render_template('mapping/list.html', spotify_albums=spotify_albums,
                           release_group=release_group)


@mapping_bp.route('/spotify/add')
def spotify():
    release_group_id = request.args.get('release_group_id')
    if not release_group_id:
        return redirect(url_for('frontend.index'))

    release_group = musicbrainz.get_release_group_by_id(release_group_id)
    if not release_group:
        flash(gettext("Only existing release groups can be mapped to Spotify!"), 'error')
        return redirect(url_for('search.index'))

    page = int(request.args.get('page', default=1))
    if page < 1:
        return redirect(url_for('.spotify'))
    limit = 16
    offset = (page - 1) * limit

    # Removing punctuation from the string
    punctuation_map = dict((ord(char), None) for char in string.punctuation)
    query = unicode(release_group['title']).translate(punctuation_map)
    # Searching...
    response = spotify_api.search(query, 'album', limit, offset).get('albums')
    return render_template('mapping/spotify.html', release_group=release_group, search_results=response.get('items'),
                           page=page, limit=limit, count=response.get('total'))


@mapping_bp.route('/spotify/confirm', methods=['GET', 'POST'])
@login_required
def spotify_confirm():
    """Confirmation page for adding new Spotify mapping."""
    release_group_id = request.args.get('release_group_id')
    release_group = musicbrainz.get_release_group_by_id(release_group_id)
    if not release_group:
        flash(gettext("Only existing release groups can be mapped to Spotify!"), 'error')
        return redirect(url_for('search.index'))

    spotify_ref = request.args.get('spotify_ref', default=None)
    if not spotify_ref:
        flash(gettext("You need to select an album from Spotify!"), 'error')
        return redirect(url_for('.spotify', release_group_id=release_group_id))

    spotify_id = parse_spotify_id(spotify_ref)
    if not spotify_id:
        flash(gettext("You need to specify a correct link to this album on Spotify!"), 'error')
        return redirect(url_for('.spotify', release_group_id=release_group_id))

    album = spotify_api.get_album(spotify_id)
    if not album or album.get('error'):
        flash(gettext("You need to specify existing album from Spotify!"), 'error')
        return redirect(url_for('.spotify', release_group_id=release_group_id))

    if request.method == 'POST':
        # TODO(roman): Check values that are returned by add_mapping (also take a look at related JS).
        mbspotify.add_mapping(release_group_id, 'spotify:album:%s' % spotify_id, current_user.id)
        flash(gettext("Spotify mapping has been added!"), 'success')
        return redirect(url_for('.spotify_list', release_group_id=release_group_id))

    return render_template('mapping/confirm.html', release_group=release_group, spotify_album=album)


@mapping_bp.route('/spotify/report', methods=['GET', 'POST'])
@login_required
def spotify_report():
    """Endpoint for reporting incorrect Spotify mappings.

    Shows confirmation page before submitting report to mbspotify.
    """
    release_group_id = request.args.get('release_group_id')
    spotify_id = request.args.get('spotify_id')
    spotify_uri = "spotify:album:" + spotify_id

    # Checking if release group exists
    release_group = musicbrainz.get_release_group_by_id(release_group_id)
    if not release_group:
        flash(gettext("Can't find release group with that ID!"), 'error')
        return redirect(url_for('.spotify_list', release_group_id=release_group_id))

    # Checking if release group is mapped to Spotify
    spotify_mappings = mbspotify.mappings(str(release_group_id))
    if not (spotify_uri in spotify_mappings):
        flash(gettext("This album is not mapped to Spotify yet!"), 'error')
        return redirect(url_for('.spotify_list', release_group_id=release_group_id))

    if request.method == 'POST':
        mbspotify.vote(release_group_id, spotify_uri, current_user.id)
        flash(gettext("Incorrect Spotify mapping has been reported. Thank you!"), 'success')
        return redirect(url_for('.spotify_list', release_group_id=release_group_id))

    else:
        album = spotify_api.get_album(spotify_id)
        if not album or album.get('error'):
            flash(gettext("You need to specify existing album from Spotify!"), 'error')
            return redirect(url_for('.spotify_list', release_group_id=release_group_id))

        return render_template('mapping/report.html', release_group=release_group, spotify_album=album)


def parse_spotify_id(spotify_ref):
    """Extracts Spotify ID out of reference to an album on Spotify.

    Supported reference types:
      - Spotify URI (spotify:album:6IH6co1QUS7uXoyPDv0rIr)
      - HTTP link (http://open.spotify.com/album/6IH6co1QUS7uXoyPDv0rIr)
    """
    # Spotify URI
    if spotify_ref.startswith('spotify:album:'):
        return spotify_ref[14:]

    # Link to Spotify
    # TODO(roman): Improve checking there. See https://bitbucket.org/metabrainz/critiquebrainz/pull-request/167/cb-115-support-for-different-types-of/activity#comment-2757329
    if spotify_ref.startswith('http://') or spotify_ref.startswith('https://'):
        if spotify_ref.endswith('/'):
            spotify_ref = spotify_ref[:-1]
        return os.path.split(urlparse(spotify_ref).path)[-1]

    # TODO(roman): Raise exception if failed to parse!
