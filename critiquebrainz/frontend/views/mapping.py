"""
Package mapping is basically an interface for mbspotify project.

It allows users to create mappings between release groups and albums on
Spotify. These mappings are then used to show embedded Spotify player on some
pages. See https://github.com/metabrainz/mbspotify for more info about this
project.
"""
import os.path
import string
import urllib.parse

from flask import Blueprint, render_template, request, url_for, redirect, current_app
from flask_babel import gettext
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound, BadRequest, ServiceUnavailable

import critiquebrainz.frontend.external.musicbrainz_db.release_group as mb_release_group
import critiquebrainz.frontend.external.spotify as spotify_api
from critiquebrainz.frontend import flash
from critiquebrainz.frontend.external import mbspotify
from critiquebrainz.frontend.external.exceptions import ExternalServiceException
from brainzutils.musicbrainz_db.exceptions import NoDataFoundException

mapping_bp = Blueprint('mapping', __name__)


@mapping_bp.route('/<uuid:release_group_id>')
def spotify_list(release_group_id):
    """This view lists all Spotify albums mapped to a specified release group."""
    spotify_mappings = mbspotify.mappings(str(release_group_id))
    # Converting Spotify URIs to IDs
    spotify_ids = []
    for mapping in spotify_mappings:
        spotify_ids.append(mapping[14:])

    if spotify_ids:
        try:
            spotify_albums = spotify_api.get_multiple_albums(spotify_ids)
        except ExternalServiceException as e:
            raise ServiceUnavailable(e)
    else:
        spotify_albums = {}
    try:
        release_group = mb_release_group.get_release_group_by_id(str(release_group_id))
    except NoDataFoundException:
        raise NotFound("Can't find release group with a specified ID.")
    return render_template('mapping/list.html', spotify_albums=spotify_albums,
                           release_group=release_group)


@mapping_bp.route('/spotify/add')
def spotify_add():
    release_group_id = request.args.get('release_group_id')
    if not release_group_id:
        return redirect(url_for('frontend.index'))
    try:
        release_group = mb_release_group.get_release_group_by_id(release_group_id)
    except NoDataFoundException:
        flash.error(gettext("Only existing release groups can be mapped to Spotify!"))
        return redirect(url_for('search.index'))

    page = int(request.args.get('page', default=1))
    if page < 1:
        return redirect(url_for('.spotify_add'))
    limit = 16
    offset = (page - 1) * limit

    # Removing punctuation from the string
    punctuation_map = dict((ord(char), None) for char in string.punctuation)
    query = release_group['title'].translate(punctuation_map)
    # Searching...
    try:
        response = spotify_api.search(query, item_types='album', limit=limit, offset=offset).get('albums')
    except ExternalServiceException as e:
        current_app.logger.error("Error while searching Spotify API: %s", str(e), exc_info=True)
        raise ServiceUnavailable(e)

    albums_ids = [x['id'] for x in response['items']]
    try:
        full_response = spotify_api.get_multiple_albums(albums_ids)
    except ExternalServiceException as e:
        current_app.logger.error("Error while getting albums from Spotify: %s", str(e), exc_info=True)
        raise ServiceUnavailable(e)

    search_results = [full_response[id] for id in albums_ids if id in full_response]

    return render_template('mapping/spotify.html', release_group=release_group,
                           search_results=search_results, page=page, limit=limit,
                           count=response.get('total'))


@mapping_bp.route('/spotify/confirm', methods=['GET', 'POST'])
@login_required
def spotify_confirm():
    """Confirmation page for adding new Spotify mapping."""
    release_group_id = request.args.get('release_group_id')
    if not release_group_id:
        raise BadRequest("Didn't provide `release_group_id`!")
    try:
        release_group = mb_release_group.get_release_group_by_id(release_group_id)
    except NoDataFoundException:
        flash.error(gettext("Only existing release groups can be mapped to Spotify!"))
        return redirect(url_for('search.index'))

    spotify_ref = request.args.get('spotify_ref', default=None)
    if not spotify_ref:
        flash.error(gettext("You need to select an album from Spotify!"))
        return redirect(url_for('.spotify_add', release_group_id=release_group_id))

    try:
        spotify_id = parse_spotify_id(spotify_ref)
    except UnsupportedSpotifyReferenceTypeException:
        flash.error(gettext("You need to specify a correct link to this album on Spotify!"))
        return redirect(url_for('.spotify_add', release_group_id=release_group_id))
    except Exception:
        raise BadRequest("Could not parse Spotify ID!")

    try:
        album = spotify_api.get_album(spotify_id)
    except ExternalServiceException:
        flash.error(gettext("You need to specify existing album from Spotify!"))
        return redirect(url_for('.spotify_add', release_group_id=release_group_id))

    if request.method == 'POST':
        # TODO(roman): Check values that are returned by add_mapping (also take a look at related JS).
        res, error = mbspotify.add_mapping(release_group_id, 'spotify:album:%s' % spotify_id, current_user.id)
        if res:
            flash.success(gettext("Spotify mapping has been added!"))
        else:
            flash.error(gettext("Could not add Spotify mapping!"))
            current_app.logger.error("Failed to create new Spotify mapping! Error: {}".format(error))
        return redirect(url_for('.spotify_list', release_group_id=release_group_id))

    return render_template('mapping/confirm.html', release_group=release_group, spotify_album=album)


@mapping_bp.route('/spotify/report', methods=['GET', 'POST'])
@login_required
def spotify_report():
    """Endpoint for reporting incorrect Spotify mappings.

    Shows confirmation page before submitting report to mbspotify.
    """
    release_group_id = request.args.get('release_group_id')
    if not release_group_id:
        raise BadRequest("Didn't provide `release_group_id`!")

    spotify_id = request.args.get('spotify_id')
    if not spotify_id:
        raise BadRequest("Didn't provide `spotify_id`!")

    spotify_uri = "spotify:album:" + spotify_id

    # Checking if release group exists
    try:
        release_group = mb_release_group.get_release_group_by_id(release_group_id)
    except NoDataFoundException:
        raise NotFound("Can't find release group with a specified ID.")

    # Checking if release group is mapped to Spotify
    spotify_mappings = mbspotify.mappings(str(release_group_id))
    if spotify_uri not in spotify_mappings:
        flash.error(gettext("This album is not mapped to Spotify yet!"))
        return redirect(url_for('.spotify_list', release_group_id=release_group_id))

    if request.method == 'POST':
        res, error = mbspotify.vote(release_group_id, spotify_uri, current_user.id)
        if res:
            flash.success(gettext("Incorrect Spotify mapping has been reported. Thank you!"))
        else:
            flash.error(gettext("Could not report incorrect Spotify mapping!"))
            current_app.logger.error("Failed to report incorrect Spotify mapping! Error: {}".format(error))
        return redirect(url_for('.spotify_list', release_group_id=release_group_id))

    try:
        album = spotify_api.get_album(spotify_id)
    except ExternalServiceException:
        flash.error(gettext("You need to specify existing album from Spotify!"))
        return redirect(url_for('.spotify_list', release_group_id=release_group_id))

    return render_template('mapping/report.html', release_group=release_group, spotify_album=album)


class UnsupportedSpotifyReferenceTypeException(Exception):
    """Exception for Unsupported Spotify Reference Types."""


def parse_spotify_id(spotify_ref):
    """Extracts Spotify ID out of reference to an album on Spotify.

    Supported reference types:
      - Spotify URI (spotify:album:6IH6co1QUS7uXoyPDv0rIr)
      - HTTP link (http://open.spotify.com/album/6IH6co1QUS7uXoyPDv0rIr)

    Returns:
        parsed spotify id (ex. "6IH6co1QUS7uXoyPDv0rIr") if supported reference types are provided, else raises Exception
    """
    try:
        if spotify_ref.startswith('spotify:album:'):
            # Spotify URI
            return spotify_ref[14:]

        if spotify_ref.startswith('http://') or spotify_ref.startswith('https://'):
            # Link to Spotify
            if spotify_ref.endswith('/'):
                spotify_ref = spotify_ref[:-1]
            return os.path.split(urllib.parse.urlparse(spotify_ref).path)[-1]

        raise UnsupportedSpotifyReferenceTypeException("Unsupported Spotify Reference Type!")
    except Exception as e:
        current_app.logger.error('Error "{}" occurred while parsing Spotify ID!'.format(e))
        # Raise exception if failed to parse!
        raise
