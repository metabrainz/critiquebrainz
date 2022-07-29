from critiquebrainz.frontend.external.bookbrainz_db import publisher
from critiquebrainz.data.testing import DataTestCase


class PublisherTestCase(DataTestCase):
    def setUp(self):

        super(PublisherTestCase, self).setUp()
        self.bbid1 = "6b331e7e-9d95-48a1-aed0-3b9ced7b1812"
        self.bbid2 = "21d66111-9f4b-4352-9356-058d972b1343"
        self.bbid3 = "9571beef-3233-45a5-b580-da08055a0c5b" 

    def test_get_publisher_by_bbid(self):
        publisher_info = publisher.get_publisher_by_bbid(self.bbid1)
        self.assertEqual(publisher_info["bbid"], self.bbid1)
        self.assertEqual(publisher_info["name"], "Penguin Group")
        self.assertEqual(publisher_info["sort_name"], "Penguin Group")
        self.assertEqual(publisher_info["publisher_type"], "Publisher")

    def test_fetch_multiple_publishers(self):
        publishers = publisher.fetch_multiple_publishers([self.bbid2, self.bbid3])
        self.assertEqual(len(publishers), 2)
        self.assertEqual(publishers[self.bbid2]["bbid"], self.bbid2)
        self.assertEqual(publishers[self.bbid2]["name"], "Macmillan")
        self.assertEqual(publishers[self.bbid2]["publisher_type"], "Imprint")
        self.assertEqual(publishers[self.bbid3]["bbid"], self.bbid3)
        self.assertEqual(publishers[self.bbid3]["name"], "DC Comics, Inc")
        self.assertEqual(publishers[self.bbid3]["publisher_type"], "Publisher") 

