from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data.utils import explode_db_uri


class DataUtilsTestCase(DataTestCase):

    def test_explode_db_uri(self):
        uri = "postgresql://cb_user:cb_password@localhost:5432/cb"
        hostname, db_name, username, password = explode_db_uri(uri)

        self.assertEqual(hostname, "localhost")
        self.assertEqual(db_name, "cb")
        self.assertEqual(username, "cb_user")
        self.assertEqual(password, "cb_password")
