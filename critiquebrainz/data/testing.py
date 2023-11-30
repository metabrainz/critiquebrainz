import os

from flask_testing import TestCase

from critiquebrainz.data.utils import create_all, drop_tables, drop_types, clear_tables
from critiquebrainz.frontend import create_app


class DataTestCase(TestCase):

    def create_app(self):
        app = create_app(config_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'test_config.py'))
        return app

    def setUp(self):
        self.reset_db()
        # TODO(roman): Add stuff form fixtures.

    def tearDown(self):
        pass

    @staticmethod
    def reset_db():
        clear_tables()
