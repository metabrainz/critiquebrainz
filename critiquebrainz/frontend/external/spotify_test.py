from brainzutils import cache
from critiquebrainz.frontend.testing import FrontendTestCase
from critiquebrainz.frontend.external import spotify


class FakeSpotifyResponse:
    def __init__(self, query):
        self.url = spotify._BASE_URL + query

    def json(self):
        return dict(url=self.url)

    @classmethod
    def fromSpotifyIds(cls, spotify_ids):
        response = []
        for spotify_id in spotify_ids:
            response.append({'id': spotify_id, 'data': spotify._BASE_URL + spotify_id})
        return dict(albums=response)


class SpotifyTestCase(FrontendTestCase):

    def setUp(self):
        super(SpotifyTestCase, self).setUp()
        spotify._get = lambda query: FakeSpotifyResponse(query).json()
        spotify.cache.get = lambda key, namespace=None: None

    def test_search(self):
        self.assertDictEqual(
            spotify.search("Random name!", item_types='album'),
            dict(url="https://api.spotify.com/v1/search?q=Random%20name%21&type=album&limit=20&offset=0"))

    def test_album(self):
        self.assertDictEqual(
            spotify.get_album('random-spotify-id'),
            dict(url="https://api.spotify.com/v1/albums/random-spotify-id"))

    def test_get_multiple_albums(self):
        spotify_ids = ['0Y7qkJVZ06tS2GUCDptzyW']
        if cache.get_many(spotify_ids, 'spotify_albums'):
            cache.delete_many(spotify_ids, 'spotify_albums')

        spotify._get = lambda query: FakeSpotifyResponse.fromSpotifyIds(spotify_ids)
        albums = spotify.get_multiple_albums(spotify_ids)
        self.assertDictEqual(albums[spotify_ids[0]], {
            'id': spotify_ids[0],
            'data': spotify._BASE_URL + spotify_ids[0],
        })

        albums = cache.get_many(spotify_ids, 'spotify_albums')
        self.assertListEqual(list(albums.keys()), spotify_ids)

        # test if cached result is returned properly
        albums = spotify.get_multiple_albums(spotify_ids)
        self.assertDictEqual(albums[spotify_ids[0]], {
            'id': spotify_ids[0],
            'data': spotify._BASE_URL + spotify_ids[0],
        })
