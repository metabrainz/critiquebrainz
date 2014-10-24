"""
This module provides interface to Spotify ID mapper - mbspotify.

Source code of mbspotify is available at https://github.com/metabrainz/mbspotify.
"""
import json
import requests

_base_url = ""
_key = ""


def init(base_url, access_key):
    global _base_url, _key
    _base_url = base_url
    _key = access_key


def mappings(mbid=None):
    """Get mappings to Spotify for a specified MusicBrainz ID."""
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(_base_url + 'mapping', headers=headers, data=json.dumps({'mbid': mbid}))
    return resp.json().get('mapping')


def add_mapping(mbid, spotify_uri, user_id):
    """Submit new spotify mapping."""
    # TODO: Catch errors during submission.
    requests.post(_base_url + 'mapping/add?key=' + _key, headers={'Content-Type': 'application/json'},
                  data=json.dumps({'mbid': str(mbid), 'spotify_uri': spotify_uri, 'user': str(user_id)}))


def vote(mbid, user_id):
    """Submit report about incorrect Spotify mapping."""
    # TODO: Catch errors during voting.
    requests.post(_base_url + 'mapping/vote?key=' + _key, headers={'Content-Type': 'application/json'},
                  data=json.dumps({'mbid': str(mbid), 'user': str(user_id)}))
