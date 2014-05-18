import json
import requests


class MBSpotifyClient(object):
    """Provides interface to Spotify ID mapper."""

    def __init__(self, base_url):
        self.base_url = base_url

    def mapping(self, mbids=[]):
        try:
            headers = {'Content-type': 'application/json'}
            resp = requests.post(self.base_url + "mapping", headers=headers,
                                 data=json.dumps({'mbids': mbids}))
            return resp.json().get('mapping')
        except Exception as e:
            return []

    def add_mapping(self, mbid, spotify_uri, user_id):
        headers = {'Content-type': 'application/json'}
        resp = requests.post(self.base_url + "mapping/add", headers=headers,
                             data=json.dumps({'mbid': str(mbid), 'spotify_uri': spotify_uri, 'user': str(user_id)}))

    def report(self, mbid, user_id):
        headers = {'Content-type': 'application/json'}
        resp = requests.post(self.base_url + "mapping/vote", headers=headers,
                             data=json.dumps({'mbid': str(mbid), 'user': user_id}))
