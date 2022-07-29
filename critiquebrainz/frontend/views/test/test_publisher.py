from unittest import mock

import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.frontend.testing import FrontendTestCase

class PublisherViewsTestCase(FrontendTestCase):

	def setUp(self):
		super(PublisherViewsTestCase, self).setUp()
		self.user = User(db_users.get_or_create(1, "Tester", new_user_data={
			"display_name": "test user",
		}))
		self.license = db_license.create(
			id='Test',
			full_name='Test License',
		)

	def test_publisher_page(self):
		db_review.create(
			user_id=self.user.id,
			entity_id='6b331e7e-9d95-48a1-aed0-3b9ced7b1812',
			entity_type='bb_publisher',
			text='This is a test review',
			is_draft=False,
			license_id=self.license['id'],
			language='en',
		)
		response = self.client.get('/publisher/6b331e7e-9d95-48a1-aed0-3b9ced7b1812')
		self.assert200(response)
		self.assertIn("Penguin Group", str(response.data))
		# Test if there is a review from test user
		self.assertIn('test user', str(response.data))

	def test_publisher_page_not_found(self):
		# No such mbid returns an error.
		response = self.client.get('/publisher/6b331e7e-9d95-48a1-aed0-3b9ced7b1811')
		self.assert404(response)
