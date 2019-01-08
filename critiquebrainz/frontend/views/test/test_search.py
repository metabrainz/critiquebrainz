from unittest.mock import MagicMock
from critiquebrainz.frontend.testing import FrontendTestCase
from critiquebrainz.frontend.external import musicbrainz

class SearchViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(SearchViewsTestCase, self).setUp()
        musicbrainz.search_artists = MagicMock(return_value=(1, [{
            'id': 'b10bbbfc-cf9e-42e0-be17-e2c3e1d2600d',
            'type': 'Group',
            'name': 'The Beatles',
            'sort-name': 'Beatles, The',
            'country': 'GB'
        }]))

    def test_search_page(self):
        response = self.client.get("/search/?query=The+Beatles&type=artist")
        self.assert200(response)
        self.assertIn("Beatles, The", str(response.data))
