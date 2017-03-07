from critiquebrainz.frontend.testing import FrontendTestCase
from critiquebrainz.db.user import User
import critiquebrainz.db.users as db_users


class UserViewsTestCase(FrontendTestCase):

    def test_reviews(self):
        user = User(db_users.get_or_create("aef06569-098f-4218-a577-b413944d9493", new_user_data={
            "display_name": "Tester",
        }))
        response = self.client.get("/user/%s" % user.id)
        self.assert200(response)
        self.assertIn("Tester", str(response.data))

    def test_info(self):
        user = User(db_users.get_or_create("aef06569-098f-4218-a577-b413944d9493", new_user_data={
            "display_name": "Tester",
        }))
        response = self.client.get("/user/%s/info" % user.id)
        self.assert200(response)
        self.assertIn("Tester", str(response.data))
