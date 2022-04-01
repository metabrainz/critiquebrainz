from unittest import mock

import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.frontend.testing import FrontendTestCase


class ReleaseGroupViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ReleaseGroupViewsTestCase, self).setUp()
        self.user = User(db_users.get_or_create(1, "Tester", new_user_data={
            "display_name": "test user",
        }))
        self.license = db_license.create(
            id='Test',
            full_name='Test License',
        )

    def test_release_group_page(self):
        db_review.create(
            user_id=self.user.id,
            entity_id='1eff4a06-056e-4dc7-91c4-0cbc5878f3c3',
            entity_type='release_group',
            text='This is a test review',
            is_draft=False,
            license_id=self.license['id'],
            language='en',
        )
        response = self.client.get('/release-group/1eff4a06-056e-4dc7-91c4-0cbc5878f3c3')
        self.assert200(response)
        self.assertIn('Strobe Light', str(response.data))
        # Test if there is a review from test user
        self.assertIn('test user', str(response.data))

    def test_releasegroup_page_not_found(self):
        # No such mbid returns an error.
        response = self.client.get('/release-group/1eff4a06-056e-4dc7-91c4-0cbc58780000')
        self.assert404(response)