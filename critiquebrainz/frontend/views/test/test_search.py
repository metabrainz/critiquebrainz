from critiquebrainz.frontend.testing import FrontendTestCase


class SearchViewsTestCase(FrontendTestCase):

    def test_search_page(self):
        response = self.client.get("/search/?query=The+Beatles&type=artist")
        self.assert200(response)
        self.assertIn("Beatles, The", response.data)
