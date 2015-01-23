from rauth import OAuth2Service
from flask import request, session, url_for, flash
from flask_login import current_user
from flask_babel import gettext
import critiquebrainz
from critiquebrainz.data.model.user import User
from critiquebrainz.utils import generate_string
import xml.etree.ElementTree as ET
import logging
import json

_musicbrainz = None
_session_key = None


def init(client_id, client_secret, session_key='musicbrainz'):
    global _musicbrainz, _session_key
    _musicbrainz = OAuth2Service(
        name='musicbrainz',
        base_url="https://musicbrainz.org/",
        authorize_url="https://musicbrainz.org/oauth2/authorize",
        access_token_url="https://musicbrainz.org/oauth2/token",
        client_id=client_id,
        client_secret=client_secret,
    )
    _session_key = session_key


def get_user():
    """Function should fetch user data from database, or, if necessary, create it, and return it."""
    s = _musicbrainz.get_auth_session(data={
        'code': _fetch_data('code'),
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('login.musicbrainz_post', _external=True)
    }, decoder=json.loads)

    access_token_response = s.access_token_response.json()
    if 'refresh_token' in access_token_response:
        # We get a refresh token the first time exchange of an authorization code happens.
        refresh_token = s.access_token_response.json()['refresh_token']
    else:
        refresh_token = None

    data = s.get('oauth2/userinfo').json()
    return User.get_or_create(
        musicbrainz_id=data.get('sub'),
        display_name=data.get('sub'),
        mb_refresh_token=refresh_token,
    )


def get_release_group_rating(release_group):
    """Get current user's rating for a specified release group.

    Returns:
        Rating that user have given to that release group, or None if there is
        it's not rated yet.
    """
    try:
        s = _get_auth_session()
        data = s.get('ws/2/release-group/%s?inc=user-ratings&fmt=json' % release_group).json()
        return data['user-rating']['value'] if 'user-rating' in data else None
    except (MissingTokenException, KeyError) as e:
        logging.warning(e)
        flash(gettext("Failed to get your rating of this release group from "
                      "MusicBrainz. You might want to sign in again."), 'warning')


def submit_release_group_rating(release_group, rating):
    """Submit user's rating for a specified release group.

    Rating is a number between 0 and 100, at intervals of 20 (20 per "star").
    Submitting a rating of 0 will remove the user's rating.
    """
    # Building XML content
    NS = "http://musicbrainz.org/ns/mmd-2.0#"
    root = ET.Element("{%s}metadata" % NS)
    e_list = ET.SubElement(root, "{%s}release-group-list" % NS)
    e_xml = ET.SubElement(e_list, "{%s}release-group" % NS)
    e_xml.set("{%s}id" % NS, release_group)
    rating_xml = ET.SubElement(e_xml, "{%s}user-rating" % NS)
    rating_xml.text = str(rating)
    xml = ET.tostring(root, "utf-8")

    try:
        s = _get_auth_session()
        s.post('ws/2/rating?client=%s' % _get_client_string(), data=xml,
               headers={'Content-Type': 'application/xml;charset=UTF-8'})
    except (MissingTokenException, KeyError) as e:
        logging.warning(e)
        flash(gettext("Failed to submit your rating to MusicBrainz. "
                      "You might want to sign in again."), 'warning')


def _get_auth_session():
    """Creates auth session using current user's refresh token."""
    # TODO: If possible, use refresh token only if access_token is expired.
    if not current_user.mb_refresh_token:
        raise MissingTokenException("MusicBrainz OAuth refresh token is missing!")

    return _musicbrainz.get_auth_session(data={
        'refresh_token': current_user.mb_refresh_token,
        'grant_type': 'refresh_token',
        'redirect_uri': url_for('login.musicbrainz_post', _external=True)
    }, decoder=json.loads)


def get_authentication_uri(approval_prompt='auto'):
    """Prepare and return uri to authentication service login form.

    Args:
        approval_prompt: Either 'auto' or 'force'. Second forces approval form
            display. Default is 'auto'.
    """
    csrf = generate_string(20)
    _persist_data(csrf=csrf)
    params = {
        'response_type': 'code',
        'redirect_uri': url_for('login.musicbrainz_post', _external=True),
        'approval_prompt': approval_prompt,
        'access_type': 'offline',
        'scope': 'profile rating',
        'state': csrf,
    }
    return _musicbrainz.get_authorize_url(**params)


def validate_post_login():
    """Function validating parameters passed in uri query after redirection from login form.
    Should return True, if everything is ok, or False, if something went wrong.
    """
    if request.args.get('error'):
        return False
    if _fetch_data('csrf') != request.args.get('state'):
        return False
    code = request.args.get('code')
    if not code:
        return False
    _persist_data(code=code)
    return True


def _persist_data(**kwargs):
    """Save data in session."""
    if _session_key not in session:
        session[_session_key] = dict()
    session[_session_key].update(**kwargs)
    session.modified = True


def _fetch_data(key, default=None):
    """Fetch data from session."""
    if _session_key not in session:
        return None
    else:
        return session[_session_key].get(key, default)


def _get_client_string():
    return 'critiquebrainz-' + str(critiquebrainz.__version__)


class MissingTokenException(Exception):
    pass
