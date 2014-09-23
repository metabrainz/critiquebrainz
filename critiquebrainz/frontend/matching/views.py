from flask import Blueprint, render_template, request, url_for, redirect, flash, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext
from critiquebrainz.frontend.apis import musicbrainz, spotify, mbspotify
from urlparse import urlparse
import os.path
import string

matching_bp = Blueprint('matching', __name__)


@matching_bp.route('/spotify/<uuid:release_group_id>', endpoint='spotify')
def spotify_matching_handler(release_group_id):
    # Checking if release group is already matched
    spotify_mapping = mbspotify.mapping([str(release_group_id)])
    if len(spotify_mapping) > 0:
        flash(gettext("Thanks, but this album is already matched to Spotify!"))
        return redirect(url_for('release_group.entity', id=release_group_id))

    release_group = musicbrainz.release_group_details(release_group_id)
    if not release_group:
        flash(gettext("Only existing release groups can be matched to Spotify!"), 'error')
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
    response = spotify.search(query, 'album', limit, offset).get('albums')
    return render_template('matching/spotify.html', release_group=release_group, search_results=response.get('items'),
                           page=page, limit=limit, count=response.get('total'))


@matching_bp.route('/spotify/<uuid:release_group_id>/confirm', methods=['GET', 'POST'], endpoint='spotify_confirm')
@login_required
def spotify_matching_submit_handler(release_group_id):
    # Checking if release group is already matched
    spotify_mapping = mbspotify.mapping([str(release_group_id)])
    if len(spotify_mapping) > 0:
        flash(gettext("Thanks, but this album is already matched to Spotify!"))
        return redirect(url_for('release_group.entity', id=release_group_id))

    release_group = musicbrainz.release_group_details(release_group_id)
    if not release_group:
        flash(gettext("Only existing release groups can be matched to Spotify!"), 'error')
        return redirect(url_for('search.index'))

    spotify_ref = request.args.get('spotify_ref', default=None)
    if not spotify_ref:
        flash(gettext("You need to select an album from Spotify!"), 'error')
        return redirect(url_for('.spotify', release_group_id=release_group_id))

    spotify_id = parse_spotify_id(spotify_ref)
    if not spotify_id:
        flash(gettext("You need to specify a correct link to this album on Spotify!"), 'error')
        return redirect(url_for('.spotify', release_group_id=release_group_id))

    album = spotify.album(spotify_id)
    if not album or album.get('error'):
        flash(gettext("You need to specify existing album from Spotify!"), 'error')
        return redirect(url_for('.spotify', release_group_id=release_group_id))

    if request.method == 'POST':
        mbspotify.add_mapping(release_group_id, 'spotify:album:%s' % spotify_id, current_user.id)
        flash(gettext("Spotify mapping has been added!"), 'success')
        return redirect(url_for('release_group.entity', id=release_group_id))

    return render_template('matching/confirm.html', release_group=release_group, spotify_album=album)


@matching_bp.route('/spotify/<uuid:release_group_id>/report', methods=['POST'], endpoint='spotify_report')
@login_required
def spotify_matching_report_handler(release_group_id):
    # Checking if release group exists
    release_group = musicbrainz.release_group_details(release_group_id)
    if not release_group:
        return jsonify(success=False, error=gettext("Can't find release group with that ID!"))

    # Checking if release group is matched
    spotify_mapping = mbspotify.mapping([str(release_group_id)])
    if len(spotify_mapping) < 1:
        return jsonify(success=False, error=gettext("This album is not matched to Spotify yet!"))

    mbspotify.vote(release_group_id, current_user.id)
    return jsonify(success=True)


def parse_spotify_id(spotify_ref):
    # Spotify URI
    if spotify_ref.startswith('spotify:album:'):
        return spotify_ref[14:]

    # Link to Spotify
    # TODO: Improve checking there. See https://bitbucket.org/metabrainz/critiquebrainz/pull-request/167/cb-115-support-for-different-types-of/activity#comment-2757329
    if spotify_ref.startswith('http://') or spotify_ref.startswith('https://'):
        if spotify_ref.endswith('/'):
            spotify_ref = spotify_ref[:-1]
        return os.path.split(urlparse(spotify_ref).path)[-1]
