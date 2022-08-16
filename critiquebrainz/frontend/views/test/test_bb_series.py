import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.frontend.testing import FrontendTestCase

class SeriesViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(SeriesViewsTestCase, self).setUp()
        self.user = User(db_users.get_or_create(1, "Tester", new_user_data={
            "display_name": "test user",
        }))
        self.license = db_license.create(
            id='Test',
            full_name='Test License',
        )

    def test_series_page(self):
        db_review.create(
            user_id=self.user.id,
            entity_id='e6f48cbd-26de-4c2e-a24a-29892f9eb3be',
            entity_type='bb_series',
            text='This is a test review',
            is_draft=False,
            license_id=self.license['id'],
            language='en',
        )
        response = self.client.get('/series/e6f48cbd-26de-4c2e-a24a-29892f9eb3be')
        self.assert200(response)
        self.assertIn("Harry Potter", str(response.data))
        # Test if there is a review from test user
        self.assertIn('test user', str(response.data))

    def test_series_page_not_found(self):
        # No such mbid returns an error.
        response = self.client.get('/series/e6f48cbd-26de-4c2e-a24a-29892f9eb3b1')
        self.assert404(response)
