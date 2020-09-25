from http import HTTPStatus
from unittest.mock import MagicMock

import requests
from brainzutils import cache

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

    def test_get(self):
        # test when _fetch_access_token returns acceptable token
        requests.get = MagicMock(return_value=self.ok_response)
        spotify._fetch_access_token = MagicMock(return_value="valid-token")
        self.assertDictEqual(spotify._get("test-query"), self.some_albums_response)
        spotify._fetch_access_token.assert_called_with(refresh=False)

        # test when _fetch_access_token returns expired token
        requests.get = MagicMock(return_value=self.unauth_response)
        spotify._fetch_access_token = MagicMock(return_value="expired-token")
        with self.assertRaises(spotify.SpotifyUnexpectedResponseException):
            spotify._get("test-query")
        spotify._fetch_access_token.assert_called_with(refresh=True)

    def test_fetch_access_token(self):
        cache.set = MagicMock()
        requests.post = MagicMock(return_value=self.fresh_token_response)

        # token present in cache
        cache.get = MagicMock(return_value=self.cached_token["access_token"])
        # use cached token
        self.assertEqual(spotify._fetch_access_token(refresh=False), self.cached_token["access_token"])
        # force fetch fresh token (used for case when token is expired)
        self.assertEqual(spotify._fetch_access_token(refresh=True), self.fresh_token["access_token"])

        # token not present in cache
        cache.get = MagicMock(return_value=None)
        # fresh token should be fetched, whatever be the value of 'refresh'
        self.assertEqual(spotify._fetch_access_token(refresh=False), self.fresh_token["access_token"])
        self.assertEqual(spotify._fetch_access_token(refresh=True), self.fresh_token["access_token"])

        # should raise SpotifyException if could not fetch fresh token
        requests.post = MagicMock(return_value=MockResponse(content={}))
        with self.assertRaises(spotify.SpotifyException):
            spotify._fetch_access_token(refresh=True)

    def test_search(self):
        # results are in cache
        cache.get = MagicMock(return_value=self.all_albums)
        self.assertDictEqual(spotify.search("test-query"), self.all_albums)

        # results are not in cache
        cache.get = MagicMock(return_value=None)
        spotify._get = MagicMock(return_value=self.all_albums)
        self.assertDictEqual(spotify.search(query="Test Artist"), self.all_albums)

    def test_get_album(self):
        # results are in cache
        cache.get = MagicMock(return_value=self.all_albums)
        self.assertDictEqual(spotify.get_album("test-spotify-id"), self.all_albums)

        # results are not in cache
        cache.get = MagicMock(return_value=None)
        spotify._get = MagicMock(return_value=self.all_albums)
        self.assertDictEqual(spotify.get_album("test-spotify-id"), self.all_albums)

    def test_get_multiple_albums(self):
        # if no spotify ids are sent
        self.assertDictEqual(spotify.get_multiple_albums([]), {})

        # all ids are in cache
        cache.get_many = MagicMock(return_value=self.all_albums)
        self.assertDictEqual(spotify.get_multiple_albums(self.all_spotify_ids), self.all_albums)

        # some ids are not in cache
        cache.get_many = MagicMock(return_value=self.some_albums)
        # _get sends an unexpected response
        spotify._get = MagicMock(return_value={})
        with self.assertRaises(spotify.SpotifyUnexpectedResponseException):
            spotify.get_multiple_albums(self.all_spotify_ids)
        # _get sends expected response
        spotify._get = MagicMock(return_value=self.some_albums_response)
        self.assertDictEqual(spotify.get_multiple_albums(self.all_spotify_ids), self.all_albums)
