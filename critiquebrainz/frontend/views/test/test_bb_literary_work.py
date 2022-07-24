from unittest import mock

import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.frontend.testing import FrontendTestCase

class LiteraryWorkViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(LiteraryWorkViewsTestCase, self).setUp()
        self.user = User(db_users.get_or_create(1, "Tester", new_user_data={
            "display_name": "test user",
        }))
        self.license = db_license.create(
            id='Test',
            full_name='Test License',
        )
    
    def test_literary_work_page(self):
        db_review.create(
            user_id=self.user.id,
            entity_id='65e71f2e-7245-42df-b93e-89463a28f75c',
            entity_type='bb_literary_work',
            text='This is a test review',
            is_draft=False,
            license_id=self.license['id'],
            language='en',
        )
        response = self.client.get('/literary-work/65e71f2e-7245-42df-b93e-89463a28f75c')
        self.assert200(response)
        self.assertIn("Harry Potter and the Philosopher's Stone", str(response.data))
        # Test if there is a review from test user
        self.assertIn('test user', str(response.data))
    
    def test_literary_work_page_not_found(self):
        # No such mbid returns an error.
        response = self.client.get('/literary-work/56efa555-abd5-4ccb-89a6-ff9d9021971s')
        self.assert404(response)