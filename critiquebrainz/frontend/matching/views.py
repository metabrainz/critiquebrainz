from flask import Blueprint, render_template, request, url_for, redirect, flash, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext
from critiquebrainz.frontend.apis import musicbrainz, spotify, mbspotify
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


@matching_bp.route('/spotify/<uuid:release_group_id>/confirm', methods=['GET'], endpoint='spotify_confirm')
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

    spotify_uri = request.args.get('spotify_uri', default=None)
    if not spotify_uri:
        flash(gettext("You need to select an album from Spotify!"), 'error')
        return redirect(url_for('.spotify', release_group_id=release_group_id))

    if not spotify_uri.startswith("spotify:album:"):
        flash(gettext("You need to specify correct Spotify URI for this album!"), 'error')
        return redirect(url_for('.spotify', release_group_id=release_group_id))

    album = spotify.album(spotify_uri[14:])
    if not album or album.get('error'):
        flash(gettext("You need to specify existing album from Spotify!"), 'error')
        return redirect(url_for('.spotify', release_group_id=release_group_id))

    return render_template('matching/confirm.html', release_group=release_group, spotify_album=album)


@matching_bp.route('/spotify/<uuid:release_group_id>/confirm', methods=['POST'], endpoint='spotify_submit')
@login_required
def spotify_matching_submit_handler(release_group_id):
    # Checking if release group exists
    release_group = musicbrainz.release_group_details(release_group_id)
    if not release_group:
        flash(gettext("Only existing release groups can be matched to Spotify!"), 'error')
        return redirect(url_for('search.index'))

    # Checking if release group is already matched
    spotify_mapping = mbspotify.mapping([str(release_group_id)])
    if len(spotify_mapping) > 0:
        flash(gettext("Thanks, but this album is already matched to Spotify!"))
        return redirect(url_for('release_group.entity', id=release_group_id))

    spotify_uri = request.args.get('spotify_uri', default=None)
    if not spotify_uri:
        return redirect(url_for('.spotify', release_group_id=release_group_id))
    mbspotify.add_mapping(release_group_id, spotify_uri, current_user.id)
    flash(gettext('Connection is added!'), 'success')
    return redirect(url_for('release_group.entity', id=release_group_id))


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
