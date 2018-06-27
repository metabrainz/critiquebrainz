from critiquebrainz.data.testing import DataTestCase
import critiquebrainz.db.oauth_client as db_oauth_client
import critiquebrainz.db.users as db_users
from critiquebrainz.db.exceptions import NoDataFoundException
from critiquebrainz.db.user import User


class OAuthClientTestCase(DataTestCase):
    def setUp(self):
        super(OAuthClientTestCase, self).setUp()
        self.user = User(db_users.get_or_create("Author", new_user_data={
            "display_name": "Author",
        }))
        self.application = dict(
            name="Some Application",
            desc="Created for some purpose",
            website="http://example.com/",
            redirect_uri="https://example.com/redirect/",
        )

    def create_dummy_application(self):
        db_oauth_client.create(user_id=self.user.id, **self.application)
        client = db_users.clients(self.user.id)[0]
        return client

    def test_create(self):
        client = self.create_dummy_application()
        self.assertEqual(client["name"], "Some Application")
        self.assertEqual(len(client["client_id"]), 20)
        self.assertEqual(len(client["client_secret"]), 40)

    def test_delete(self):
        oauth_client = self.create_dummy_application()
        db_oauth_client.delete(oauth_client["client_id"])
        with self.assertRaises(NoDataFoundException):
            db_oauth_client.get_client(oauth_client["client_id"])

    def test_update(self):
        oauth_client = self.create_dummy_application()
        db_oauth_client.update(
            client_id=oauth_client["client_id"],
            name="Testing Application",
            desc="An app for testing",
        )
        client = db_oauth_client.get_client(oauth_client["client_id"])
        self.assertEqual(client["name"], "Testing Application")
        self.assertEqual(client["desc"], "An app for testing")
