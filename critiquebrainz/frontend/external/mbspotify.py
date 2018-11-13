"""
This module provides interface to Spotify ID mapper - mbspotify.

Source code of mbspotify is available at https://github.com/metabrainz/mbspotify.
"""
import json
import requests
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from flask_babel import lazy_gettext
from brainzutils import cache
from critiquebrainz.frontend import flash

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

    data = cache.get(mbid, _CACHE_NAMESPACE)
    if not data:
        try:
            session = requests.Session()
            session.mount(_base_url, HTTPAdapter(max_retries=2))
            resp = session.post(
                url=_base_url + 'mapping',
                headers={'Content-Type': 'application/json'},
                data=json.dumps({'mbid': mbid}),
            )
            resp.raise_for_status()
            data = resp.json().get('mappings')
        except RequestException:
            flash.warn(lazy_gettext("Spotify mapping server is unavailable. You will not see an embedded player."))
            return []
        cache.set(key=mbid, namespace=_CACHE_NAMESPACE, val=data)
    return data


def add_mapping(mbid, spotify_uri, user_id):
    """Submit new Spotify mapping.

    Returns:
        Returns two values. First one is a boolean that indicates whether the submission has been successful.
        The second is an exception in case errors occur. If there are no errors, this value is None.
    """
    try:
        if _base_url is None or _key is None:
            raise ValueError("Missing MBSPOTIFY_BASE_URI or MBSPOTIFY_ACCESS_KEY.")
        session = requests.Session()
        session.mount(_base_url, HTTPAdapter(max_retries=2))
        resp = session.post(_base_url + 'mapping/add?key=' + _key,
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'mbid': str(mbid), 'spotify_uri': str(spotify_uri), 'user': str(user_id)}))
        cache.delete(mbid, _CACHE_NAMESPACE)
        return resp.status_code == 200, None
    except (RequestException, ValueError) as e:
        return False, e


def vote(mbid, spotify_uri, user_id):
    """Submit report about incorrect Spotify mapping.

    Returns:
        Returns two values. First one is a boolean that indicates whether the submission has been successful.
        The second is an exception in case errors occur. If there are no errors, this value is None.
    """
    try:
        if _base_url is None or _key is None:
            raise ValueError("Missing MBSPOTIFY_BASE_URI or MBSPOTIFY_ACCESS_KEY.")
        session = requests.Session()
        session.mount(_base_url, HTTPAdapter(max_retries=2))
        resp = session.post(_base_url + 'mapping/vote?key=' + _key,
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'mbid': str(mbid), 'spotify_uri': str(spotify_uri), 'user': str(user_id)}))
        cache.delete(mbid, _CACHE_NAMESPACE)
        return resp.status_code == 200, None
    except (RequestException, ValueError) as e:
        return False, e
