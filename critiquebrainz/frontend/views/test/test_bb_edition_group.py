from unittest import mock

import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.frontend.testing import FrontendTestCase

class EditionGroupViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(EditionGroupViewsTestCase, self).setUp()
        self.user = User(db_users.get_or_create(1, "Tester", new_user_data={
            "display_name": "test user",
        }))
        self.license = db_license.create(
            id='Test',
            full_name='Test License',
        )
    
    def test_edition_group_page(self):
        db_review.create(
            user_id=self.user.id,
            entity_id='9f49df73-8ee5-4c5f-8803-427c9b216d8f',
            entity_type='bb_edition_group',
            text='This is a test review',
            is_draft=False,
            license_id=self.license['id'],
            language='en',
        )
        response = self.client.get('/edition-group/9f49df73-8ee5-4c5f-8803-427c9b216d8f')
        self.assert200(response)
        self.assertIn('Harry Potter and the Deathly Hallows', str(response.data))
        # Test if there is a review from test user
        self.assertIn('test user', str(response.data))
    
    def test_editiongroup_page_not_found(self):
        # No such mbid returns an error.
        response = self.client.get('/edition-group/9f49df73-8ee5-4c5f-8803-427c9b2160000')
        self.assert404(response)