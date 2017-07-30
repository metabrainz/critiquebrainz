import os
from flask_testing import TestCase
from critiquebrainz.frontend import create_app

class MBDatabaseTestCase(TestCase):

    def create_app(self):
        app = create_app(config_path=os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '../../..', 'test_config.py'
        ))
        return app
