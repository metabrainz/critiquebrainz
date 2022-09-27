import os

from critiquebrainz import db
from critiquebrainz.ws.oauth import oauth

from flask_testing import TestCase

from critiquebrainz.data.utils import ADMIN_SQL_DIR
from critiquebrainz.frontend import create_app


class FrontendTestCase(TestCase):

    def create_app(self):
        app = create_app(config_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'test_config.py'))
        oauth.init_app(app)
        return app

    def setUp(self):
        self.reset_db()
        # TODO(roman): Add stuff form fixtures.

    def tearDown(self):
        pass

    @staticmethod
    def reset_db():
        db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'reset_tables.sql'))

    def temporary_login(self, user):
        """Based on: http://stackoverflow.com/a/16238537."""
        with self.client.session_transaction() as session:
            session['_user_id'] = user.id
            session['_fresh'] = True
