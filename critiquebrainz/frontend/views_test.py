from critiquebrainz.testing import ServerTestCase


class ViewsTestCase(ServerTestCase):

    def test_home_page(self):
        self.client.get("/")

    def test_404(self):
        self.client.get("/404")
