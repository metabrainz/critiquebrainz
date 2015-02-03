from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import utils


class DataUtilsTestCase(DataTestCase):

    def test_explode_db_uri(self):
        uri = "postgresql://cb_user:cb_password@localhost:5432/cb"
        hostname, db_name, username, password = utils.explode_db_uri(uri)

        self.assertEqual(hostname, "localhost")
        self.assertEqual(db_name, "cb")
        self.assertEqual(username, "cb_user")
        self.assertEqual(password, "cb_password")

    def test_slugify(self):
        self.assertEqual(utils.slugify(u'CC BY-NC-SA 3.0'), 'cc-by-nc-sa-30')
        self.assertEqual(utils.slugify(u'CC BY-SA 3.0'), 'cc-by-sa-30')
