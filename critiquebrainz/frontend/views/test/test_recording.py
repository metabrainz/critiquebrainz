from unittest.mock import MagicMock

import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
import critiquebrainz.frontend.external.musicbrainz_db.recording as mb_recording
from critiquebrainz.db.user import User
from critiquebrainz.frontend.testing import FrontendTestCase


class RecordingViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(RecordingViewsTestCase, self).setUp()
        mb_recording.get_recording_by_id = MagicMock()
        mb_recording.get_recording_by_id.return_value = {
            'id': '442ddce2-ffa1-4865-81d2-b42c40fec7c5',
            'name': 'Dream Come True',
            'length': 229.0,
            'artists': [
                {
                    'id': '164f0d73-1234-4e2c-8743-d77bf2191051',
                    'name': 'Kanye West',
                    'join_phrase': ' feat. '
                },
                {
                    'id': '75a72702-a5ef-4513-bca5-c5b944903546',
                    'name': 'John Legend'
                }
            ],
            'artist-credit-phrase': 'Kanye West feat. John Legend'
        }
        self.user = User(db_users.get_or_create(1, "Tester", new_user_data={"display_name": "test user"}))
        self.license = db_license.create(id='Test', full_name='Test License')

    def test_recording_page(self):
        db_review.create(
            user_id=self.user.id,
            entity_id='442ddce2-ffa1-4865-81d2-b42c40fec7c5',
            entity_type='recording',
            text='This is a test review',
            is_draft=False,
            license_id=self.license['id'],
            language='en',
        )
        response = self.client.get('/recording/8ef859e3-feb2-4dd1-93da-22b91280d768')
        self.assert200(response)
        self.assertIn('Dream Come True', str(response.data))
        # Test if there is a review from test user
        self.assertIn('test user', str(response.data))
