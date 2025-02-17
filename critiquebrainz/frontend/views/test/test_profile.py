import critiquebrainz.db.license as db_license
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.frontend.testing import FrontendTestCase


class ProfileViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ProfileViewsTestCase, self).setUp()
        self.license = db_license.create(
            id="CC BY-SA 4.0",
            full_name="Created so we can fill the form correctly.",
        )
        self.user = User(db_users.get_or_create(1, "Tester", new_user_data={
            "display_name": "Tester",
        }))

    def test_edit(self):
        data = dict(
            display_name="Some User",
            email='someuser@somesite.com'
        )

        response = self.client.post('/profile/edit', data=data,
                                    query_string=data, follow_redirects=True)
        self.assertIn("Please sign in to access this page.", str(response.data))

        self.temporary_login(self.user)
        response = self.client.post('/profile/edit', data=data,
                                    query_string=data, follow_redirects=True)
        self.assert200(response)

        # because the g global persists for entire duration of the test, we need to manually logout/login
        # the user again for the current_user to be refreshed. in production, this would happen automatically
        # as the current_user is loaded at the start of each request/request context.
        self.temporary_login(self.user)

        response = self.client.get(f'/user/{self.user.id}')
        self.assert200(response)
        self.assertIn(data['display_name'], str(response.data))

    def test_delete(self):
        self.temporary_login(self.user)
        response = self.client.post('/profile/delete', follow_redirects=True)
        self.assert200(response)
