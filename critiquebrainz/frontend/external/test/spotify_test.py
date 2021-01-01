from http import HTTPStatus
from unittest import mock

from critiquebrainz.frontend.external import spotify
from critiquebrainz.frontend.testing import FrontendTestCase


class MockResponse:
    """ Class for mocking response to requests """

    def __init__(self, content=None, status_code=None):
        self.content = content
        self.status_code = status_code

    def json(self):
        return self.content

    def __getstate__(self):
        return {
            'status_code': self.status_code,
            'content': self.content,
        }


class SpotifyTestCase(FrontendTestCase):

    def setUp(self):
        super(SpotifyTestCase, self).setUp()
        self.all_spotify_ids = ['test-spotify-id-1', 'test-spotify-id-2']
        self.some_albums = {
            'test-spotify-id-1': {
                'id': 'test-spotify-id-1',
                'name': 'Test Album 1',
            },
        }
        self.all_albums = {
            'test-spotify-id-1': {
                'id': 'test-spotify-id-1',
                'name': 'Test Album 1',
            },
            'test-spotify-id-2': {
                'id': 'test-spotify-id-2',
                'name': 'Test Album 2',
            },
        }
        self.some_albums_response = {
            'albums': [{
                'id': 'test-spotify-id-2',
                'name': 'Test Album 2',
            }]
        }
        self.ok_response = MockResponse(content=self.some_albums_response, status_code=HTTPStatus.OK)
        self.unauth_response = MockResponse(status_code=HTTPStatus.UNAUTHORIZED)
        self.cached_token = {
            'access_token': 'cached-access-token',
        }
        self.cached_token_response = MockResponse(content=self.cached_token)
        self.fresh_token = {
            'access_token': 'fresh-access-token',
        }
        self.fresh_token_response = MockResponse(content=self.fresh_token)

    @mock.patch('critiquebrainz.frontend.external.spotify._fetch_access_token')
    @mock.patch('requests.get')
    def test_valid_get(self, requests_get, _fetch_access_token):
        # test when _fetch_access_token returns acceptable token
        requests_get.return_value = self.ok_response
        _fetch_access_token.return_value = "valid-token"
        self.assertDictEqual(spotify._get("test-query"), self.some_albums_response)
        _fetch_access_token.assert_called_with(refresh=False)

        # test when _fetch_access_token returns expired token
        _fetch_access_token.reset_mock()
        requests_get.return_value = self.unauth_response
        _fetch_access_token.return_value = "expired-token"
        with self.assertRaises(spotify.SpotifyUnexpectedResponseException):
            spotify._get("test-query")
        _fetch_access_token.assert_called_with(refresh=True)

    @mock.patch('brainzutils.cache.set')
    @mock.patch('brainzutils.cache.get')
    @mock.patch('requests.post')
    def test_fetch_access_token(self, requests_post, cache_get, cache_set):
        requests_post.return_value = self.fresh_token_response

        # token present in cache
        cache_get.return_value = self.cached_token["access_token"]
        # use cached token
        self.assertEqual(spotify._fetch_access_token(refresh=False), self.cached_token["access_token"])
        # force fetch fresh token (used for case when token is expired)
        self.assertEqual(spotify._fetch_access_token(refresh=True), self.fresh_token["access_token"])

        # token not present in cache
        cache_get.reset_mock()
        cache_get.return_value = None
        # fresh token should be fetched, whatever be the value of 'refresh'
        self.assertEqual(spotify._fetch_access_token(refresh=False), self.fresh_token["access_token"])
        self.assertEqual(spotify._fetch_access_token(refresh=True), self.fresh_token["access_token"])

        # should raise SpotifyException if could not fetch fresh token
        requests_post.reset_mock()
        requests_post.return_value = MockResponse(content={})
        with self.assertRaises(spotify.SpotifyException):
            spotify._fetch_access_token(refresh=True)

    @mock.patch('critiquebrainz.frontend.external.spotify._get')
    @mock.patch('brainzutils.cache.get')
    def test_search(self, cache_get, spotify_get):
        # results are in cache
        cache_get.return_value = self.all_albums
        self.assertDictEqual(spotify.search("test-query"), self.all_albums)

        # results are not in cache
        cache_get.reset_mock()
        cache_get.return_value = None
        spotify_get.return_value = self.all_albums
        self.assertDictEqual(spotify.search(query="Test Artist"), self.all_albums)

    @mock.patch('critiquebrainz.frontend.external.spotify._get')
    @mock.patch('brainzutils.cache.get')
    def test_get_album(self, cache_get, spotify_get):
        # results are in cache
        cache_get.return_value = self.all_albums
        self.assertDictEqual(spotify.get_album("test-spotify-id"), self.all_albums)

        # results are not in cache
        cache_get.reset_mock()
        cache_get.return_value = None
        spotify_get.return_value = self.all_albums
        self.assertDictEqual(spotify.get_album("test-spotify-id"), self.all_albums)

    @mock.patch('critiquebrainz.frontend.external.spotify._get')
    @mock.patch('brainzutils.cache.get_many')
    def test_get_multiple_albums(self, cache_get_many, spotify_get):
        # if no spotify ids are sent
        self.assertDictEqual(spotify.get_multiple_albums([]), {})

        # all ids are in cache
        cache_get_many.return_value = self.all_albums
        self.assertDictEqual(spotify.get_multiple_albums(self.all_spotify_ids), self.all_albums)

        # some ids are not in cache
        cache_get_many.reset_mock()
        cache_get_many.return_value = self.some_albums
        # _get sends an unexpected response
        spotify_get.return_value = {}
        with self.assertRaises(spotify.SpotifyUnexpectedResponseException):
            spotify.get_multiple_albums(self.all_spotify_ids)
        # _get sends expected response
        spotify_get.reset_mock()
        spotify_get.return_value = self.some_albums_response
        self.assertDictEqual(spotify.get_multiple_albums(self.all_spotify_ids), self.all_albums)
