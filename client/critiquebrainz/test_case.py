from flask.ext.testing import TestCase
from critiquebrainz import app


class ClientTestCase(TestCase):

    def create_app(self):
        return app
