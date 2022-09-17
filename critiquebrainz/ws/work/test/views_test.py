from brainzutils import cache

import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.ws.testing import WebServiceTestCase


class WorkViewsTestCase(WebServiceTestCase):

    def setUp(self):
        super(WorkViewsTestCase, self).setUp()

        self.work_id1 = "0e5a48f3-7d21-365c-bfb7-98d9865ea1dd"
        self.work_id2 = "fd881e93-c199-4c86-81a7-cabc044948d0"

        self.user = User(db_users.get_or_create(1, "Tester", new_user_data={
            "display_name": "test user",
        }))
        self.another_user = User(db_users.get_or_create(2, "Hacker!", new_user_data={
            "display_name": "test hacker",
        }))
        self.license = db_license.create(
            id="CC BY-SA 3.0",
            full_name="Created so we can fill the form correctly.",
        )
        self.review = dict(
            entity_id=self.work_id1,
            entity_type='work',
            user_id=self.user.id,
            text="Testing! This text should be on the page.",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )
        self.review2 = dict(
            entity_id=self.work_id2,
            entity_type='work',
            user_id=self.user.id,
            text="Testing! This text should be on the page.",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )

    def create_dummy_review(self):
        return db_review.create(**self.review)

    def create_dummy_review2(self):
        return db_review.create(**self.review2)

    def test_work_endpoint(self):
        review = self.create_dummy_review()
        response = self.client.get('/work/0e5a48f3-7d21-365c-bfb7-98d9865ea1dd')

        self.assert200(response)
        self.assertIn(review['text'], response.json['top_reviews'][0]['text'])

        self.assertEqual(5, response.json['average_rating'])
        self.assertEqual(1, response.json['reviews_count'])

        # Test for a work that doesn't exist
        response = self.client.get('/work/0e5a48f3-7d21-365c-bfb7-98d9865ea1d1')
        self.assert404(response)

    def test_work_user_reviews(self):
        review = self.create_dummy_review()
        response = self.client.get('/work/0e5a48f3-7d21-365c-bfb7-98d9865ea1dd?username=%s' % self.user.musicbrainz_username)

        self.assert200(response)
        self.assertIn(review['text'], response.json['user_review']['text'])

    def test_user_cache_tracking(self):
        track_key = cache.gen_key("entity_api", self.work_id2, self.user.musicbrainz_username, "user_review")

        # Make sure the cache is empty
        self.client.get('/work/fd881e93-c199-4c86-81a7-cabc044948d0?username=%s' % self.user.musicbrainz_username)
        cache_value = cache.get(track_key, namespace="Review")
        self.assertEqual([], cache_value)

        review = self.create_dummy_review2()

        # Check if the cache is populated after the request
        self.client.get('/work/fd881e93-c199-4c86-81a7-cabc044948d0?username=%s' % self.user.musicbrainz_username)
        cache_value = cache.get(track_key, namespace="Review")

        self.assertIn(review['text'], cache_value['text'])
