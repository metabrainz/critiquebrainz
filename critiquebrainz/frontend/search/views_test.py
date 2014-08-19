from critiquebrainz.frontend.testing import FrontendTestCase


class ViewsTestCase(FrontendTestCase):

    def test_search_page(self):
        response = self.client.get("/search/?query=The+Beatles&type=artist")
        assert response.status_code == 200
        assert "Beatles, The" in response.data
