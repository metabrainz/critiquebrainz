from unittest import mock

import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.frontend.testing import FrontendTestCase

class AuthorViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(AuthorViewsTestCase, self).setUp()
        self.user = User(db_users.get_or_create(1, "Tester", new_user_data={
            "display_name": "test user",
        }))
        self.license = db_license.create(
            id='Test',
            full_name='Test License',
        )

    def test_author_page(self):
        db_review.create(
            user_id=self.user.id,
            entity_id='5df290b8-ecd5-44fb-8d05-70e291133688',
            entity_type='bb_author',
            text='This is a test review',
            is_draft=False,
            license_id=self.license['id'],
            language='en',
        )
        response = self.client.get('/author/5df290b8-ecd5-44fb-8d05-70e291133688')
        self.assert200(response)
        self.assertIn("Charles Dickens", str(response.data))
        # Test if there is a review from test user
        self.assertIn('test user', str(response.data))

    def test_author_page_not_found(self):
        # No such mbid returns an error.
        response = self.client.get('/author/5df290b8-ecd5-44fb-8d05-70e291133631')
        self.assert404(response)
