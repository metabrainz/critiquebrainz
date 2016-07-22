from flask_testing import TestCase
from critiquebrainz.frontend import create_app
from critiquebrainz.data import db


class DataTestCase(TestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.create_all()
        # TODO(roman): Add stuff form fixtures.

    def tearDown(self):
        db.session.remove()
        db.drop_all()
