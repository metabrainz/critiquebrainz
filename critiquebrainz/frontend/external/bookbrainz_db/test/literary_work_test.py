from critiquebrainz.frontend.external.bookbrainz_db import literary_work
from critiquebrainz.data.testing import DataTestCase


class LiteraryWorkTestCase(DataTestCase):
    def setUp(self):

        super(LiteraryWorkTestCase, self).setUp()
        self.bbid1 = "56efa555-abd5-4ccb-89a6-ff9d9021971f"
        self.bbid2 = "65e71f2e-7245-42df-b93e-89463a28f75c"
        self.bbid3 = "0e03bc2a-2867-4687-afee-e211ece30772"
        self.bbid4 = "14b910e7-c003-491b-923c-eeadd272d29b"

    def test_get_literary_work_by_bbid(self):
        literary_work_info = literary_work.get_literary_work_by_bbid(self.bbid1)
        self.assertEqual(literary_work_info["bbid"], self.bbid1)
        self.assertEqual(literary_work_info["name"], "Assassin's Creed: Brotherhood")
        self.assertEqual(literary_work_info["sort_name"], "Assassin's Creed: Brotherhood")
        self.assertEqual(literary_work_info["work_type"], "Novel")

    def test_fetch_multiple_literary_works(self):
        literary_works = literary_work.fetch_multiple_literary_works([self.bbid2, self.bbid3])
        self.assertEqual(len(literary_works), 2)
        self.assertEqual(literary_works[self.bbid2]["bbid"], self.bbid2)
        self.assertEqual(literary_works[self.bbid2]["name"], "Harry Potter and the Philosopher’s Stone")
        self.assertEqual(literary_works[self.bbid2]["work_type"], "Novel")
        self.assertEqual(literary_works[self.bbid3]["bbid"], self.bbid3)
        self.assertEqual(literary_works[self.bbid3]["name"], "Oliver Twist")
        self.assertEqual(literary_works[self.bbid3]["work_type"], "Novel")

    def test_fetch_edition_groups_for_works(self):
        edition_group_bbids_1 = literary_work.fetch_edition_groups_for_works(self.bbid2)
        self.assertEqual(len(edition_group_bbids_1), 2)
        self.assertEqual(edition_group_bbids_1[0], "02ae4cfc-6412-4693-93b1-e24dce5e31f9")
        self.assertEqual(edition_group_bbids_1[1], "5876d2ee-2654-4c03-a2e3-599ace14531a")

        edition_group_bbids_2 = literary_work.fetch_edition_groups_for_works(self.bbid4)
        self.assertEqual(len(edition_group_bbids_2), 0)
