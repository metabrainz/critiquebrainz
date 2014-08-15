import json
import requests


class MBSpotifyClient(object):
    """Provides interface to Spotify ID mapper - MBSpotify.
    Source code of this application is available at https://github.com/metabrainz/mbspotify.
    """

    def __init__(self, base_url, access_key):
        self.base_url = base_url
        self.key = access_key

    def mapping(self, mbids=None):
        """Get mapping to Spotify for a set of MusicBrainz IDs."""
        if mbids is None:
            mbids = []
        try:
            headers = {'Content-Type': 'application/json'}
            resp = requests.post(self.base_url + 'mapping', headers=headers, data=json.dumps({'mbids': mbids}))
            return resp.json().get('mapping')
        except Exception as e:
            # TODO: Catch errors properly and return informative errors.
            return []

    def add_mapping(self, mbid, spotify_uri, user_id):
        """Submit new spotify mapping."""
        # TODO: Catch errors during submission.
        requests.post(self.base_url + 'mapping/add?key=' + self.key, headers={'Content-Type': 'application/json'},
                      data=json.dumps({'mbid': str(mbid), 'spotify_uri': spotify_uri, 'user': str(user_id)}))

    def vote(self, mbid, user_id):
        """Submit report about incorrect Spotify mapping."""
        # TODO: Catch errors during voting.
        requests.post(self.base_url + 'mapping/vote?key=' + self.key, headers={'Content-Type': 'application/json'},
                      data=json.dumps({'mbid': str(mbid), 'user': str(user_id)}))
