from datetime import datetime, timedelta
from critiquebrainz.data.testing import DataTestCase
import critiquebrainz.db.oauth_grant as db_oauth_grant
import critiquebrainz.db.oauth_client as db_oauth_client
import critiquebrainz.db.users as db_users
import critiquebrainz.db.exceptions as db_exceptions
from critiquebrainz.db.user import User


class OAuthGrantTestCase(DataTestCase):

    def setUp(self):
        super(OAuthGrantTestCase, self).setUp()
        self.user = User(db_users.get_or_create('tester_1', new_user_data={
            "display_name": "test",
        }))
        db_oauth_client.create(
            user_id=self.user.id,
            name="Test App",
            desc="Application for testing",
            website="https://example.com",
            redirect_uri="https://example.com/oauth",
        )
        self.oauth_client = db_users.clients(self.user.id)[0]

    def test_create(self):
        self.assertEqual(len(db_oauth_grant.list_grants()), 0)
        db_oauth_grant.create(
            client_id=self.oauth_client["client_id"],
            code="Test Code",
            redirect_uri="https://example.com",
            expires=datetime.now() + timedelta(seconds=200),
            user_id=self.user.id,
            scopes=None,
        )
        self.assertEqual(len(db_oauth_grant.list_grants()), 1)

    def test_list(self):
        oauth_grant = db_oauth_grant.create(
            client_id=self.oauth_client["client_id"],
            code="Test Code",
            redirect_uri="https://example.com",
            expires=datetime.now() + timedelta(seconds=200),
            user_id=self.user.id,
            scopes=None,
        )
        self.assertEqual(len(db_oauth_grant.list_grants(client_id=self.oauth_client["client_id"])), 1)
        self.assertEqual(len(db_oauth_grant.list_grants(client_id=self.oauth_client["client_id"], code=oauth_grant["code"])), 1)

    def test_delete(self):
        oauth_grant = db_oauth_grant.create(
            client_id=self.oauth_client["client_id"],
            code="Test Code",
            redirect_uri="https://example.com",
            expires=datetime.now() + timedelta(seconds=200),
            user_id=self.user.id,
            scopes=None,
        )
        self.assertEqual(len(db_oauth_grant.list_grants(client_id=self.oauth_client["client_id"])), 1)
        db_oauth_grant.delete(client_id=self.oauth_client["client_id"], code=oauth_grant["code"])
        self.assertEqual(len(db_oauth_grant.list_grants(client_id=self.oauth_client["client_id"])), 0)

    def test_get_scopes(self):
        # Test fetching scopes of a valid grant
        oauth_grant = db_oauth_grant.create(
            client_id=self.oauth_client["client_id"],
            code="Test Code",
            redirect_uri="https://example.com",
            expires=datetime.now() + timedelta(seconds=200),
            user_id=self.user.id,
            scopes="review user",
        )
        self.assertIn("review", db_oauth_grant.get_scopes(oauth_grant["id"]))

        # Test fetching scopes of a grant that does not exist
        db_oauth_grant.delete(client_id=self.oauth_client["client_id"], code=oauth_grant["code"])
        with self.assertRaises(db_exceptions.NoDataFoundException):
            db_oauth_grant.get_scopes(oauth_grant["id"])

        # Test fetching scopes of grant with no scopes
        oauth_grant = db_oauth_grant.create(
            client_id=self.oauth_client["client_id"],
            code="Test Code",
            redirect_uri="https://example.com",
            expires=datetime.now() + timedelta(seconds=200),
            user_id=self.user.id,
            scopes=None,
        )
        self.assertEqual([], db_oauth_grant.get_scopes(oauth_grant["id"]))
