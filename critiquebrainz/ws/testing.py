from flask_testing import TestCase
from critiquebrainz.ws import create_app
from critiquebrainz.data import db
from critiquebrainz.ws.oauth import oauth
from critiquebrainz.data.model.oauth_client import OAuthClient
import os


class WebServiceTestCase(TestCase):

    def create_app(self):
        app = create_app(config_path=os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '..', 'test_config.py'
        ))
        oauth.init_app(app)
        return app

    def setUp(self):
        db.create_all()
        # TODO(roman): Add stuff form fixtures.

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_dummy_client(self, user):
        client = OAuthClient.create(
            user=user,
            name="Dummy Client",
            desc="Created for testing the webservice",
            website="http://example.com/",
            redirect_uri="http://example.com/redirect/",
        )
        return client

    def create_dummy_token(self, user, client=None):
        if client is None:
            client = self.create_dummy_client(user)
        token = oauth.generate_token(client_id=client.client_id, refresh_token="",
                                     user_id=user.id, scope="review vote user")
        return token[0]
