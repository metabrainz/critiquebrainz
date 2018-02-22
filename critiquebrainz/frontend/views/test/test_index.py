from critiquebrainz.frontend import create_app
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

    def test_flask_debugtoolbar(self):
        """ Test if flask debugtoolbar is loaded correctly

        Creating an app with default config so that debug is True
        and SECRET_KEY is defined.
        """
        app = create_app(debug=True)
        client = app.test_client()
        resp = client.get("/about")
        self.assert200(resp)
        self.assertIn("flDebug", str(resp.data))
