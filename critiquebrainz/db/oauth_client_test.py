from critiquebrainz.data.testing import DataTestCase
import critiquebrainz.db.oauth_client as db_oauth_client
from critiquebrainz.db.user import User
import critiquebrainz.db.users as db_users
from critiquebrainz.db.exceptions import NoDataFoundException


class OAuthClientTestCase(DataTestCase):
    def setUp(self):
        super(OAuthClientTestCase, self).setUp()
        self.user = User(db_users.get_or_create("Author", new_user_data={
            "display_name": "Author",
        }))

    def test_create(self):
        new_client = db_oauth_client.create(
            user_id=self.user.id,
            name="Test App",
            desc="Application for testing",
            website="https://example.com",
            redirect_uri="https://example.com/oauth",
        )

        client = db_oauth_client.get_client(new_client["client_id"])
        self.assertEqual(client["name"], "Test App")
        self.assertEqual(len(client["client_id"]), 20)
        self.assertEqual(len(client["client_secret"]), 40)

    def test_delete(self):
        oauth_client = db_oauth_client.create(
            user_id=self.user.id,
            name="Test App",
            desc="Application for testing",
            website="https://example.com",
            redirect_uri="https://example.com/oauth",
        )
        clients = db_oauth_client.get_client(oauth_client["client_id"])
        db_oauth_client.delete(oauth_client["client_id"])
        with self.assertRaises(NoDataFoundException):
            clients = db_oauth_client.get_client(oauth_client["client_id"])

    def test_update(self):
        oauth_client = db_oauth_client.create(
            user_id=self.user.id,
            name="Test App",
            desc="Application for testing",
            website="https://example.com",
            redirect_uri="https://example.com/oauth",
        )
        db_oauth_client.update(
            client_id = oauth_client["client_id"],
            name="Testing Application",
            desc="An app for testing",
        )
        client = db_oauth_client.get_client(oauth_client["client_id"])
        self.assertEqual(client["name"], "Testing Application")
        self.assertEqual(client["desc"], "An app for testing")
