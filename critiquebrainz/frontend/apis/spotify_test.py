import unittest
from critiquebrainz.frontend.apis import spotify


class FakeSpotifyResponse():
    def __init__(self, url):
        self.url = url

    def json(self):
        return dict(url=self.url)


class SpotifyTestCase(unittest.TestCase):

    def setUp(self):
        spotify.requests.get = lambda url: FakeSpotifyResponse(url)
        spotify.cache.get = lambda key: None
        spotify.generate_cache_key = lambda id, source, params: "key"

    def test_search(self):
        self.assertDictEqual(
            spotify.search("Random name!", 'album'),
            dict(url="https://api.spotify.com/v1/search?q=Random%20name%21&type=album&limit=20&offset=0"))

    def test_album(self):
        self.assertDictEqual(
            spotify.get_album('random-spotify-id'),
            dict(url="https://api.spotify.com/v1/albums/random-spotify-id"))
