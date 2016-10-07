from flask_testing import TestCase
from critiquebrainz.frontend import create_app
from critiquebrainz.data import db
import os


class FrontendTestCase(TestCase):

    def create_app(self):
        app = create_app(config_path=os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '..', 'test_config.py'
        ))
        return app

    def setUp(self):
        db.create_all()
        # TODO(roman): Add stuff form fixtures.

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def temporary_login(self, user):
        """Based on: http://stackoverflow.com/a/16238537."""
        with self.client.session_transaction() as session:
            session['user_id'] = user.id
            session['_fresh'] = True
