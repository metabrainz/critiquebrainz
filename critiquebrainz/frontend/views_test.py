from critiquebrainz.frontend.testing import FrontendTestCase


class ViewsTestCase(FrontendTestCase):

    def test_home_page(self):
        response = self.client.get("/")
        assert response.status_code == 200

    def test_404(self):
        response = self.client.get("/404")
        assert response.status_code == 404
