from critiquebrainz.frontend.testing import FrontendTestCase
from critiquebrainz.db.user import User
import critiquebrainz.db.users as db_users
import critiquebrainz.db.license as db_license


class ProfileViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ProfileViewsTestCase, self).setUp()
        self.license = db_license.create(
            id="CC BY-SA 3.0",
            full_name="Created so we can fill the form correctly.",
        )
        self.user = User(db_users.get_or_create(1, "aef06569-098f-4218-a577-b413944d9493", new_user_data={
            "display_name": "Tester",
        }))

    def test_edit(self):
        data = dict(
            display_name="Some User",
            email='someuser@somesite.com',
            show_gravatar='True',
            license_choice=self.license["id"]
        )

        response = self.client.post('/profile/edit', data=data,
                                    query_string=data, follow_redirects=True)
        self.assertIn("Please sign in to access this page.", str(response.data))

        self.temporary_login(self.user)
        response = self.client.post('/profile/edit', data=data,
                                    query_string=data, follow_redirects=True)
        self.assert200(response)
        self.assertIn(data['display_name'], str(response.data))

    def test_delete(self):
        self.temporary_login(self.user)
        response = self.client.post('/profile/delete', follow_redirects=True)
        self.assert200(response)
