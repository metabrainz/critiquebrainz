from critiquebrainz.frontend.testing import FrontendTestCase
from critiquebrainz.frontend.external import spotify

BASE_URL = "https://api.spotify.com/v1"

class FakeSpotifyResponse():
    def __init__(self, query):
        self.url = BASE_URL + query

    def json(self):
        return dict(url=self.url)


class SpotifyTestCase(FrontendTestCase):

    def setUp(self):
        super(SpotifyTestCase, self).setUp()
        spotify._get_spotify = lambda query: FakeSpotifyResponse(query).json()
        spotify.cache.get = lambda key, namespace=None: None

    def test_search(self):
        self.assertDictEqual(
            spotify.search("Random name!", 'album'),
            dict(url="https://api.spotify.com/v1/search?q=Random%20name%21&type=album&limit=20&offset=0"))

    def test_album(self):
        self.assertDictEqual(
            spotify.get_album('random-spotify-id'),
            dict(url="https://api.spotify.com/v1/albums/random-spotify-id"))
