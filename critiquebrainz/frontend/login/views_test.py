from critiquebrainz.frontend.testing import FrontendTestCase


class LoginViewsTestCase(FrontendTestCase):

    def test_login_page(self):
        response = self.client.get("/login/")
        self.assert200(response)
