from unittest import mock

from critiquebrainz.frontend.testing import FrontendTestCase


class SearchViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(SearchViewsTestCase, self).setUp()
        self.search_results = (1, [{
            'id': 'b10bbbfc-cf9e-42e0-be17-e2c3e1d2600d',
            'type': 'Group',
            'name': 'The Beatles',
            'sort-name': 'Beatles, The',
            'country': 'GB'
        }])

    @mock.patch('critiquebrainz.frontend.external.musicbrainz.search_artists')
    def test_search_page(self, search_artists):
        search_artists.return_value = self.search_results
        response = self.client.get("/search/?query=The+Beatles&type=artist")
        self.assert200(response)
        self.assertIn("Beatles, The", str(response.data))
