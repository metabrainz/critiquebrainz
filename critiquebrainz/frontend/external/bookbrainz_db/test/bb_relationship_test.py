from critiquebrainz.frontend.external.bookbrainz_db import relationships
from critiquebrainz.data.testing import DataTestCase

class BBRelationshipTestCase(DataTestCase):
    def setUP(self):
        super(BBRelationshipTestCase, self).setUp()

    def test_bb_relationship(self):
        relationship = relationships.fetch_relationships(99999999, [relationships.AUTHOR_WORK_AUTHOR_REL_ID])
        self.assertEqual(relationship[0]["label"], "Author")
        self.assertEqual(relationship[0]["source_bbid"], "e5c4e68b-bfce-4c77-9ca2-0f0a2d4d09f0")
        self.assertEqual(relationship[0]["target_bbid"], "9f49df73-8ee5-4c5f-8803-427c9b216d8f")

        relationship = relationships.fetch_relationships(99999999, [relationships.EDITION_EDITION_GROUP_EDITION_REL_ID])
        self.assertEqual(relationship, [])
