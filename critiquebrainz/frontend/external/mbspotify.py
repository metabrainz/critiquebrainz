"""
This module provides interface to Spotify ID mapper - mbspotify.

Source code of mbspotify is available at https://github.com/metabrainz/mbspotify.
"""
import json
import requests
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from critiquebrainz.frontend import flash
from flask_babel import lazy_gettext
from brainzutils import cache

_base_url = ""
_key = ""

_CACHE_NAMESPACE = "mbspotify_mappings"
_UNAVAILABLE_MSG = "Spotify mapping server is unavailable. You will not see an embedded player."


def init(base_url, access_key):
    global _base_url, _key
    _base_url = base_url
    _key = access_key


def mappings(mbid=None):
    """Get mappings to Spotify for a specified MusicBrainz ID.

    Returns:
        List containing Spotify URIs that are mapped to specified MBID.
    """
    if _base_url is None:
        flash.warn(lazy_gettext(_UNAVAILABLE_MSG))
        return []

    resp = cache.get(mbid, _CACHE_NAMESPACE)
    if not resp:
        try:
            session = requests.Session()
            session.mount(_base_url, HTTPAdapter(max_retries=2))
            resp = session.post(_base_url + 'mapping',
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps({'mbid': mbid})).json().get('mappings')
        except RequestException:
            flash.warn(lazy_gettext("Spotify mapping server is unavailable. You will not see an embedded player."))
            return []
        cache.set(key=mbid, namespace=_CACHE_NAMESPACE, val=resp)
    return resp


def add_mapping(mbid, spotify_uri, user_id):
    """Submit new Spotify mapping.

    Returns:
        Returns two values. First one is a boolean that indicates whether the submission has been successful.
        The second is an exception in case errors occur. If there are no errors, this value is None.
    """
    if _base_url is None or _key is None:
        return False, None

    try:
        session = requests.Session()
        session.mount(_base_url, HTTPAdapter(max_retries=2))
        resp = session.post(_base_url + 'mapping/add?key=' + _key,
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'mbid': str(mbid), 'spotify_uri': spotify_uri, 'user': str(user_id)}))
        cache.delete(mbid, _CACHE_NAMESPACE)
        return resp.status_code == 200, None
    except RequestException as e:
        return False, e


def vote(mbid, spotify_uri, user_id):
    """Submit report about incorrect Spotify mapping."""
    if _base_url is None or _key is None:
        return

    # TODO(roman): Catch errors during voting.
    requests.post(_base_url + 'mapping/vote?key=' + _key, headers={'Content-Type': 'application/json'},
                  data=json.dumps({
                      'mbid': str(mbid),
                      'user': str(user_id),
                      'spotify_uri': str(spotify_uri),
                  }))
    cache.delete(mbid, _CACHE_NAMESPACE)
