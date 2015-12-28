from critiquebrainz.frontend.testing import FrontendTestCase
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.oauth_client import OAuthClient


class ProfileApplicationsViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ProfileApplicationsViewsTestCase, self).setUp()
        self.user = User.get_or_create(u"Tester", u"aef06569-098f-4218-a577-b413944d9493")
        self.hacker = User.get_or_create(u"Hacker!", u"9371e5c7-5995-4471-a5a9-33481f897f9c")
        self.application = dict(
            name="Some Application",
            desc="Created for some purpose",
            website="http://example.com/",
            redirect_uri="http://example.com/redirect/",
        )

    def create_dummy_application(self):
        return OAuthClient.create(user=self.user, **self.application)

    def test_index(self):
        self.temporary_login(self.user)
        response = self.client.get('/profile/applications', follow_redirects=True)
        self.assert200(response)
        self.assertIn("No applications found", response.data)

    def test_create(self):
        self.temporary_login(self.user)
        response = self.client.post('/profile/applications/create', data=self.application,
                                    query_string=self.application, follow_redirects=True)
        self.assert200(response)
        self.assertIn(self.application['name'], response.data)

    def test_edit(self):
        app = self.create_dummy_application()

        self.application["name"] = "New Name of Application"

        self.temporary_login(self.user)
        response = self.client.post('/profile/applications/%s/edit' % app.client_id,
                                    data=self.application, query_string=self.application,
                                    follow_redirects=True)
        self.assert200(response)
        self.assertIn(self.application['name'], response.data)

    def test_delete(self):
        app = self.create_dummy_application()

        self.temporary_login(self.hacker)
        response = self.client.get('/profile/applications/%s/delete' % app.client_id,
                                   follow_redirects=True)
        self.assert404(response, "Shouldn't be able to delete other's applications.")

        self.temporary_login(self.user)
        response = self.client.get('/profile/applications/%s/delete' % app.client_id,
                                   follow_redirects=True)
        self.assert200(response)
        self.assertIn("You have deleted an application.", response.data)

    def test_token_delete(self):
        app = self.create_dummy_application()

        self.temporary_login(self.user)
        response = self.client.get('/profile/applications/%s/token/delete' % app.client_id)
        self.assertRedirects(response, '/profile/applications/')
