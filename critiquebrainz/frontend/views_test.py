from critiquebrainz.frontend.testing import FrontendTestCase


class ViewsTestCase(FrontendTestCase):

    def test_home_page(self):
        self.client.get("/")

    def test_404(self):
        self.client.get("/404")
