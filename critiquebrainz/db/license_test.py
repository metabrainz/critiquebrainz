from critiquebrainz.data.testing import DataTestCase
import critiquebrainz.db.license as db_license

class LicenseTestCase(DataTestCase):

    def test_license_create(self):
        license = db_license.create(
            id="Test",
            full_name="Test License",
            info_url="www.example.com",
        )
        self.assertEqual(license["id"], "Test")
        self.assertEqual(license["full_name"], "Test License")
        self.assertEqual(license["info_url"], "www.example.com")

    def test_delete_license(self):
        license = db_license.create(
            id="test",
            full_name="Test license",
            info_url="www.example.com",
        )
        db_license.delete(id=license["id"])
