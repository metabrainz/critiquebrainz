"""
This module provides interface to Spotify ID mapper - mbspotify.

Source code of mbspotify is available at https://github.com/metabrainz/mbspotify.
"""
import json
import requests
from requests.exceptions import RequestException
from requests.adapters import HTTPAdapter
from flask import flash
from flask_babel import gettext
from critiquebrainz.cache import cache, generate_cache_key

_base_url = ""
_key = ""


def init(base_url, access_key):
    global _base_url, _key
    _base_url = base_url
    _key = access_key


def mappings(mbid=None):
    """Get mappings to Spotify for a specified MusicBrainz ID.

    Returns:
        List containing Spotify URIs that are mapped to specified MBID.
    """
    key = generate_cache_key('mappings', source='mbspotify', params=[mbid])
    resp = cache.get(key)
    if not resp:
        try:
            session = requests.Session()
            session.mount(_base_url, HTTPAdapter(max_retries=2))
            resp = session.post(_base_url + 'mapping',
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps({'mbid': mbid})).json().get('mappings')
        except RequestException:
            flash(gettext("Spotify mapping server is unavailable. You will not see an embedded player."), "warning")
            return []
        cache.set(key, resp)
    return resp


def add_mapping(mbid, spotify_uri, user_id):
    """Submit new Spotify mapping.

    Returns:
        Returns two values. First one is a boolean that indicates whether the submission has been successful.
        The second is an exception in case errors occur. If there are no errors, this value is None.
    """
    try:
        session = requests.Session()
        session.mount(_base_url, HTTPAdapter(max_retries=2))
        resp = session.post(_base_url + 'mapping/add?key=' + _key,
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'mbid': str(mbid), 'spotify_uri': spotify_uri, 'user': str(user_id)}))
        cache.delete(generate_cache_key('mappings', source='mbspotify', params=[mbid]))
        return resp.status_code == 200, None
    except RequestException as e:
        return False, e


def vote(mbid, spotify_uri, user_id):
    """Submit report about incorrect Spotify mapping."""
    # TODO: Catch errors during voting.
    requests.post(_base_url + 'mapping/vote?key=' + _key, headers={'Content-Type': 'application/json'},
                  data=json.dumps({
                      'mbid': str(mbid),
                      'user': str(user_id),
                      'spotify_uri': str(spotify_uri),
                  }))
    cache.delete(generate_cache_key('mappings', source='mbspotify', params=[mbid]))
