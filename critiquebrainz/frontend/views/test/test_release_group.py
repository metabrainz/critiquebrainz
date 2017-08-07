from unittest.mock import MagicMock
from critiquebrainz.frontend.testing import FrontendTestCase
import critiquebrainz.frontend.external.musicbrainz_db.release_group as mb_release_group
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
import critiquebrainz.db.review as db_review
import critiquebrainz.db.license as db_license


class ReleaseGroupViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ReleaseGroupViewsTestCase, self).setUp()
        mb_release_group.get_release_group_by_id = MagicMock()
        mb_release_group.get_release_group_by_id.return_value = {
            'id': '8ef859e3-feb2-4dd1-93da-22b91280d768',
            'title': 'Collision Course',
            'first-release-year': 2004,
        }
        self.user = User(db_users.get_or_create("Tester", new_user_data={
            "display_name": "test user",
        }))
        self.license = db_license.create(
            id='Test',
            full_name='Test License',
        )

    def test_release_group_page(self):
        db_review.create(
            user_id=self.user.id,
            entity_id='8ef859e3-feb2-4dd1-93da-22b91280d768',
            entity_type='release_group',
            text='This is a test review',
            is_draft=False,
            license_id=self.license['id'],
            language='en',
        )
        response = self.client.get('/release-group/8ef859e3-feb2-4dd1-93da-22b91280d768')
        self.assert200(response)
        self.assertIn('Collision Course', str(response.data))
        # Test if there is a review from test user
        self.assertIn('test user', str(response.data))
