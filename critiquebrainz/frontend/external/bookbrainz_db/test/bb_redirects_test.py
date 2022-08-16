from critiquebrainz.frontend.external.bookbrainz_db import redirects
from critiquebrainz.data.testing import DataTestCase


class BBRedirectsTestCase(DataTestCase):

    def setUp(self):
        super(BBRedirectsTestCase, self).setUp()
        self.bbid1 = '63a40e3d-54ff-4549-9637-24959ad89241'
        self.bbid2 = 'dd40b465-931f-46ee-b2ae-28685b19f8d8'
        self.bbid3 = 'e5c4e68b-bfce-4c77-9ca2-0f0a2d4d09f0'

    def test_single_bb_redirects(self):
        # Test single redirect
        redirected_bbid = redirects.get_redirected_bbid(self.bbid1)
        self.assertEqual(redirected_bbid, 'ecdeb45d-c432-4347-94c3-f01acc799d4a')

    def test_multiple_bb_redirects(self):
        # Test multiple redirects
        redirected_bbid = redirects.get_redirected_bbid(self.bbid2)
        self.assertEqual(redirected_bbid, '7e691222-6f78-4ad6-ad5d-1a671a319fbd')

    def test_no_bb_redirects(self):
        # Test no redirects
        redirected_bbid = redirects.get_redirected_bbid(self.bbid3)
        self.assertEqual(redirected_bbid, None)
