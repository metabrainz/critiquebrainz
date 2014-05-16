import json
import requests


class MBSpotifyClient(object):
    """Provides interface to Spotify ID mapper."""

    def __init__(self, base_url):
        self.base_url = base_url

    def mapping(self, mbids=[]):
        headers = {'Content-type': 'application/json'}
        resp = requests.post(self.base_url + "mapping", data=json.dumps({'mbids': mbids}), headers=headers)
        return resp.json().get('mapping')
