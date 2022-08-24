from critiquebrainz.frontend.external.bookbrainz_db import common_entity
from critiquebrainz.data.testing import DataTestCase


class BB_MBCommonEntityTestCase(DataTestCase):

    def setUp(self):
        super(BB_MBCommonEntityTestCase, self).setUp()
        self.bbid1 = '569c0d90-28dd-413b-83e4-aaa7c27e667b'
        self.bbid2 = 'a4a6a48a-42a5-493a-9fa1-aaf6a82217e2'
        self.bbid3 = 'a99374d5-fa8b-4fab-9fec-9c0c38e8ac7c'
        self.bbid4 = '0e5a48f3-7d21-365c-bfb7-98d9865ea1dd'

    def test_get_author_for_artist(self):
        author_bbids1 = common_entity.get_author_for_artist(self.bbid1)
        self.assertEqual(len(author_bbids1), 1)
        self.assertEqual(author_bbids1[0], 'e5c4e68b-bfce-4c77-9ca2-0f0a2d4d09f0')

        author_bbids2 = common_entity.get_author_for_artist(self.bbid2)
        self.assertEqual(author_bbids2, None)

    def test_get_literary_work_for_work(self):
        work_bbids1 = common_entity.get_literary_work_for_work(self.bbid3)
        self.assertEqual(len(work_bbids1), 1)
        self.assertEqual(work_bbids1[0], 'f89e85c0-e341-4b0e-ada6-36655f5dae07')

        work_bbids2 = common_entity.get_literary_work_for_work(self.bbid4)
        self.assertEqual(work_bbids2, None)
