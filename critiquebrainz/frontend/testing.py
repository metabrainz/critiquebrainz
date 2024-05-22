import os

from critiquebrainz.frontend import create_app
from critiquebrainz.testing import ServerTestCase
from critiquebrainz.ws.oauth import oauth


class FrontendTestCase(ServerTestCase):

    @classmethod
    def create_app(cls):
        app = create_app(
            config_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'test_config.py')
        )
        oauth.init_app(app)
        app.config['TESTING'] = True
        return app
