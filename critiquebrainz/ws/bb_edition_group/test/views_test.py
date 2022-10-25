from brainzutils import cache

import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.ws.testing import WebServiceTestCase


class EditionGroupViewsTestCase(WebServiceTestCase):

    def setUp(self):
        super(EditionGroupViewsTestCase, self).setUp()

        self.edition_group_id1 = "ac4ae236-6bee-4335-9e04-21314a478f9f"
        self.edition_group_id2 = "ab87aa42-3cb7-478c-bba7-09192d04f252"

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
            entity_id=self.edition_group_id1,
            entity_type='bb_edition_group',
            user_id=self.user.id,
            text="Testing! This text should be on the page.",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )
        self.review2 = dict(
            entity_id=self.edition_group_id2,
            entity_type='bb_edition_group',
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

    def test_edition_group_endpoint(self):
        review = self.create_dummy_review()
        response = self.client.get('/edition-group/ac4ae236-6bee-4335-9e04-21314a478f9f')

        self.assert200(response)
        self.assertIn(review['text'], response.json['top_reviews'][0]['text'])

        self.assertEqual(5, response.json['average_rating'])
        self.assertEqual(1, response.json['reviews_count'])

        # Test for an edition group that doesn't exist
        response = self.client.get('/edition-group/ac4ae236-6bee-4335-9e04-21314a478f9d')
        self.assert404(response)

    def test_edition_group_user_reviews(self):
        review = self.create_dummy_review()
        response = self.client.get('/edition-group/ac4ae236-6bee-4335-9e04-21314a478f9f?username=%s' % self.user.musicbrainz_username)

        self.assert200(response)
        self.assertIn(review['text'], response.json['user_review']['text'])

    def test_user_cache_tracking(self):
        track_key = cache.gen_key("entity_api", self.edition_group_id2, self.user.musicbrainz_username, "user_review")

        # Make sure the cache is empty
        self.client.get('/edition-group/ab87aa42-3cb7-478c-bba7-09192d04f252?username=%s' % self.user.musicbrainz_username)
        cache_value = cache.get(track_key, namespace="Review")
        self.assertEqual([], cache_value)

        review = self.create_dummy_review2()

        # Check if the cache is populated after the request
        self.client.get('/edition-group/ab87aa42-3cb7-478c-bba7-09192d04f252?username=%s' % self.user.musicbrainz_username)
        cache_value = cache.get(track_key, namespace="Review")

        self.assertIn(review['text'], cache_value['text'])
