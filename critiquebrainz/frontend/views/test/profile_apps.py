from critiquebrainz.frontend.testing import FrontendTestCase
from critiquebrainz.db.user import User
import critiquebrainz.db.oauth_client as db_oauth_client
import critiquebrainz.db.users as db_users


class ProfileApplicationsViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ProfileApplicationsViewsTestCase, self).setUp()
        self.user = User(db_users.get_or_create(u"aef06569-098f-4218-a577-b413944d9493", new_user_data={
            "display_name": u"Tester",
        }))
        self.hacker = User(db_users.get_or_create(u"9371e5c7-5995-4471-a5a9-33481f897f9c", new_user_data={
            "display_name": u"Hacker!",
        }))
        self.application = dict(
            name="Some Application",
            desc="Created for some purpose",
            website="http://example.com/",
            redirect_uri="http://example.com/redirect/",
        )

    def create_dummy_application(self):
        db_oauth_client.create(user_id=self.user.id, **self.application)
        client = db_users.clients(self.user.id)[0]
        return client

    def test_index(self):
        self.temporary_login(self.user)
        response = self.client.get('/profile/applications', follow_redirects=True)
        self.assert200(response)
        self.assertIn("No applications found", str(response.data))

    def test_create(self):
        self.temporary_login(self.user)
        response = self.client.post('/profile/applications/create', data=self.application,
                                    query_string=self.application, follow_redirects=True)
        self.assert200(response)
        self.assertIn(self.application['name'], str(response.data))

    def test_edit(self):
        app = self.create_dummy_application()

        self.application["name"] = "New Name of Application"

        self.temporary_login(self.user)
        response = self.client.post('/profile/applications/%s/edit' % app["client_id"],
                                    data=self.application, query_string=self.application,
                                    follow_redirects=True)
        self.assert200(response)
        self.assertIn(self.application['name'], str(response.data))

    def test_delete(self):
        app = self.create_dummy_application()

        self.temporary_login(self.hacker)
        response = self.client.get('/profile/applications/%s/delete' % app["client_id"],
                                   follow_redirects=True)
        self.assert404(response, "Shouldn't be able to delete other's applications.")

        self.temporary_login(self.user)
        response = self.client.get('/profile/applications/%s/delete' % app["client_id"],
                                   follow_redirects=True)
        self.assert200(response)
        self.assertIn("You have deleted an application.", str(response.data))

    def test_token_delete(self):
        app = self.create_dummy_application()

        self.temporary_login(self.user)
        response = self.client.get('/profile/applications/%s/token/delete' % app["client_id"])
        self.assertRedirects(response, '/profile/applications/')
