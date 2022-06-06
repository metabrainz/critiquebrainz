from critiquebrainz.frontend.external.bookbrainz_db import edition_group
from critiquebrainz.data.testing import DataTestCase


class EditionGroupTestCase(DataTestCase):
    
    def setUp(self):
        
        super(EditionGroupTestCase, self).setUp()
        self.bbid1 = "ab87aa42-3cb7-478c-bba7-09192d04f252"
        self.bbid2 = "fd84cf1f-b288-4ea2-8e05-41257764fa6b"
        self.bbid3 = "9f49df73-8ee5-4c5f-8803-427c9b216d8f"


    def test_get_edition_group_by_bbid(self):
        edition_group_info = edition_group.get_edition_group_by_bbid(self.bbid1)
        self.assertEqual(edition_group_info["bbid"], self.bbid1)
        self.assertEqual(edition_group_info["name"], "Dragon in Exile")
        self.assertEqual(edition_group_info["sort_name"], "Dragon in Exile")
        self.assertEqual(edition_group_info["label"], "Book")


    def test_fetch_multiple_edition_groups(self):
        edition_groups = edition_group.fetch_multiple_edition_groups([self.bbid2, self.bbid3])
        self.assertEqual(len(edition_groups), 2)
        self.assertEqual(edition_groups[self.bbid2]["bbid"], self.bbid2)
        self.assertEqual(edition_groups[self.bbid2]["name"], "Stephen King Goes to the Movies")
        self.assertEqual(edition_groups[self.bbid2]["label"], "Book")
        self.assertEqual(edition_groups[self.bbid3]["bbid"], self.bbid3)
        self.assertEqual(edition_groups[self.bbid3]["name"], "Harry Potter and the Deathly Hallows")
        self.assertEqual(edition_groups[self.bbid3]["label"], "Book")