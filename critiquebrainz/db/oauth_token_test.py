from datetime import datetime, timedelta
from critiquebrainz.data.testing import DataTestCase
import critiquebrainz.db.oauth_token as db_oauth_token
import critiquebrainz.db.oauth_client as db_oauth_client
import critiquebrainz.db.users as db_users
import critiquebrainz.db.exceptions as db_exceptions
from critiquebrainz.db.user import User


class OAuthTokenTestCase(DataTestCase):

    def setUp(self):
        super(OAuthTokenTestCase, self).setUp()
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
        self.assertEqual(len(db_oauth_token.list_tokens()), 0)
        db_oauth_token.create(
            client_id=self.oauth_client["client_id"],
            access_token="Test Access Token",
            refresh_token="Test Refresh Token",
            expires=datetime.now() + timedelta(seconds=200),
            user_id=self.user.id,
            scopes=None,
        )
        self.assertEqual(len(db_oauth_token.list_tokens()), 1)

    def test_list(self):
        db_oauth_token.create(
            client_id=self.oauth_client["client_id"],
            access_token="Test Access Token",
            refresh_token="Test Refresh Token",
            expires=datetime.now() + timedelta(seconds=200),
            user_id=self.user.id,
            scopes=None,
        )
        self.assertEqual(len(db_oauth_token.list_tokens(client_id=self.oauth_client["client_id"])), 1)
        self.assertEqual(len(db_oauth_token.list_tokens(refresh_token="Test Refresh Token")), 1)

    def test_delete(self):
        db_oauth_token.create(
            client_id=self.oauth_client["client_id"],
            access_token="Test Access Token",
            refresh_token="Test Refresh Token",
            expires=datetime.now() + timedelta(seconds=200),
            user_id=self.user.id,
            scopes=None,
        )
        self.assertEqual(len(db_oauth_token.list_tokens(client_id=self.oauth_client["client_id"])), 1)
        db_oauth_token.delete(client_id=self.oauth_client["client_id"], refresh_token="Test Refresh Token")
        self.assertEqual(len(db_oauth_token.list_tokens(client_id=self.oauth_client["client_id"])), 0)

    def test_get_scopes(self):
        # Test fetching scopes of a valid token
        oauth_token = db_oauth_token.create(
            client_id=self.oauth_client["client_id"],
            access_token="Test Access Token",
            refresh_token="Test Refresh Token",
            expires=datetime.now() + timedelta(seconds=200),
            user_id=self.user.id,
            scopes="Test Scopes",
        )
        self.assertIn("Test", db_oauth_token.get_scopes(oauth_token["id"]))
        # Test fetching scopes of a token that does not exist
        db_oauth_token.delete(client_id=self.oauth_client["client_id"], refresh_token="Test Refresh Token")
        with self.assertRaises(db_exceptions.NoDataFoundException):
            db_oauth_token.get_scopes(oauth_token["id"])

        # Test fetching scopes of token with no scopes
        oauth_token = db_oauth_token.create(
            client_id=self.oauth_client["client_id"],
            access_token="Test Access Token",
            refresh_token="Test Refresh Token",
            expires=datetime.now() + timedelta(seconds=200),
            user_id=self.user.id,
            scopes=None,
        )
        self.assertEqual([], db_oauth_token.get_scopes(oauth_token["id"]))
