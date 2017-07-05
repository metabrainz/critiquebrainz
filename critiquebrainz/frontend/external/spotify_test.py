from critiquebrainz.frontend.testing import FrontendTestCase
from critiquebrainz.frontend.external import spotify


class FakeSpotifyResponse():
    def __init__(self, url):
        self.url = url

    def json(self):
        return dict(url=self.url)


class SpotifyTestCase(FrontendTestCase):

    def setUp(self):
        super(SpotifyTestCase, self).setUp()
        spotify.get_spotify = lambda url: FakeSpotifyResponse(url).json()
        spotify.cache.get = lambda key, namespace=None: None

    def test_search(self):
        self.assertDictEqual(
            spotify.search("Random name!", 'album'),
            dict(url="https://api.spotify.com/v1/search?q=Random%20name%21&type=album&limit=20&offset=0"))

    def test_album(self):
        self.assertDictEqual(
            spotify.get_album('random-spotify-id'),
            dict(url="https://api.spotify.com/v1/albums/random-spotify-id"))
