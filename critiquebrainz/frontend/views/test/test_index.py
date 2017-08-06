from critiquebrainz.frontend.testing import FrontendTestCase


class ViewsTestCase(FrontendTestCase):

    def test_home_page(self):
        response = self.client.get("/")
        self.assert200(response)

    def test_404(self):
        response = self.client.get("/404")
        self.assert404(response)

    def test_guidelines(self):
        response = self.client.get("/guidelines")
        self.assert200(response)
