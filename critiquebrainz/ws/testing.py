from flask_testing import TestCase
from critiquebrainz.ws import create_app
from critiquebrainz.data import db

from critiquebrainz.ws.oauth import oauth
from critiquebrainz.data.model.oauth_client import OAuthClient


class WebServiceTestCase(TestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['TEST_SQLALCHEMY_DATABASE_URI']
        app.config['OAUTH_TOKEN_LENGTH'] = 40
        app.config['OAUTH_GRANT_EXPIRE'] = 60
        app.config['OAUTH_TOKEN_EXPIRE'] = 3600
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
