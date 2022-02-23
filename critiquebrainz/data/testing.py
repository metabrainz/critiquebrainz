import os

from flask_testing import TestCase

from critiquebrainz.data.utils import create_all, drop_tables, drop_types
from critiquebrainz.frontend import create_app


class DataTestCase(TestCase):

    def create_app(self):
        app = create_app()
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['TESTING'] = True
        return app

    def setUp(self):
        self.reset_db()
        # TODO(roman): Add stuff form fixtures.

    def tearDown(self):
        pass

    @staticmethod
    def reset_db():
        drop_tables()
        drop_types()
        create_all()
