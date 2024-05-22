import os

import critiquebrainz.db.oauth_client as db_oauth_client
import critiquebrainz.db.users as db_users
from critiquebrainz.testing import ServerTestCase
from critiquebrainz.ws import create_app
from critiquebrainz.ws.oauth import oauth


class WebServiceTestCase(ServerTestCase):

    @classmethod
    def create_app(cls):
        app = create_app(
            config_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'test_config.py')
        )
        oauth.init_app(app)
        return app

    @staticmethod
    def create_dummy_client(user):
        db_oauth_client.create(
            user_id=user.id,
            name="Dummy Client",
            desc="Created for testing the webservice",
            website="http://example.com/",
            redirect_uri="http://example.com/redirect/",
        )
        client = db_users.clients(user.id)[0]
        return client

    def create_dummy_token(self, user, client=None):
        if client is None:
            client = self.create_dummy_client(user)
        token = oauth.generate_token(client_id=client["client_id"], refresh_token="",
                                     user_id=user.id, scope="review vote user")
        return token[0]
