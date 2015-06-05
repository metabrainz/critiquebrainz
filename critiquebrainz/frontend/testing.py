from flask_testing import TestCase
from critiquebrainz.frontend import create_app
from critiquebrainz.data import db


class FrontendTestCase(TestCase):

    def create_app(self):
        app = create_app(debug=False)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['TEST_SQLALCHEMY_DATABASE_URI']
        app.config['WTF_CSRF_ENABLED'] = False
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
