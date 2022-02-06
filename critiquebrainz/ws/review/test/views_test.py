import json
import uuid
import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.ws.testing import WebServiceTestCase


class ReviewViewsTestCase(WebServiceTestCase):

    def setUp(self):
        super(ReviewViewsTestCase, self).setUp()
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
            entity_id="6b3cd75d-7453-39f3-86c4-1441f360e121",
            entity_type='release_group',
            user_id=self.user.id,
            text="Testing! This text should be on the page.",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )

    def header(self, user):
        data = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.create_dummy_token(user)
        }
        return data

    def create_dummy_review(self):
        return db_review.create(**self.review)

    def test_review_sort(self):
        response = self.client.get('/review/', query_string={'sort': 'rating'})
        self.assert200(response)

        response = self.client.get('/review/', query_string={'sort': 'published_on'})
        self.assert200(response)

        response = self.client.get('/review/', query_string={'sort': 'popularity'})
        self.assert200(response)

        response = self.client.get('/review/', query_string={'sort': 'created'})
        self.assert200(response)

        response = self.client.get('/review/', query_string={'sort': 'hello'})
        self.assert400(response)
        self.assertEqual(response.json['description'], 'Parameter `sort`: is not valid')

    def test_review_count(self):
        resp = self.client.get('/review/').json
        self.assertEqual(resp['count'], 0)

    def test_review_entity(self):
        review = self.create_dummy_review()
        resp = self.client.get('/review/%s' % review["id"]).json
        self.assertEqual(resp['review']['id'], str(review["id"]))

    def test_review_delete(self):
        review = self.create_dummy_review()
        resp = self.client.delete('/review/%s' % review["id"], headers=self.header(self.user))
        self.assert200(resp)

    def test_review_type(self):
        review_type_all = db_review.create(
            entity_id="1b3abc15-7453-39f3-86c4-1441f360e121",
            entity_type='release_group',
            user_id=self.user.id,
            text="Testing! This text should be on the page.",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )
        review_only_rating = db_review.create(
            entity_id="2b3abc25-7453-39f3-86c4-1441f360e121",
            entity_type='release_group',
            user_id=self.user.id,
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )
        review_only_review = db_review.create(
            entity_id="3b3abc35-7453-39f3-86c4-1441f360e121",
            entity_type='release_group',
            user_id=self.user.id,
            text="Testing! This text should be on the page.",
            is_draft=False,
            license_id=self.license["id"],
        )

        response = self.client.get('/review/', query_string={'review_type': 'rating'})
        self.assert200(response)
        actual_review_ids = [review['id'] for review in response.json['reviews']]
        expected_review_ids = [str(review_type_all['id']), str(review_only_rating['id'])]
        self.assertCountEqual(actual_review_ids, expected_review_ids)

        response = self.client.get('/review/', query_string={'review_type': 'review'})
        self.assert200(response)
        actual_review_ids = [review['id'] for review in response.json['reviews']]
        expected_review_ids = [str(review_type_all['id']), str(review_only_review['id'])]
        self.assertCountEqual(actual_review_ids, expected_review_ids)

    def test_review_large_count(self):
        for _ in range(100):
            review = dict(
                entity_id=uuid.uuid4(),
                entity_type='release_group',
                user_id=self.user.id,
                text="Testing! This text should be on the page.",
                is_draft=False,
                license_id=self.license["id"],
            )
            db_review.create(**review)
        resp = self.client.get('/review/', query_string={'review_type': 'review'})
        self.assert200(resp)
        self.assertEqual(resp.json["count"], 100)
        self.assertEqual(len(resp.json["reviews"]), 50)

    def test_review_modify(self):
        review = self.create_dummy_review()

        resp = self.client.post('/review/%s' % review["id"], headers=self.header(self.another_user))
        self.assert403(resp, "Shouldn't be able to edit someone else's review.")

        # Check that a new revision is not created when review contents are not edited
        data = dict()
        resp = self.client.post('/review/%s' % review["id"], headers=self.header(self.user), data=json.dumps(data))
        self.assert200(resp)
        resp = self.client.get('/review/%s/revisions' % review["id"]).json
        self.assertEqual(len(resp['revisions']), 1)

        # Check if the passed parameter is modified and the other is not
        data = dict(text="Some updated text with length more than twenty five.")
        resp = self.client.post('/review/%s' % review["id"], headers=self.header(self.user), data=json.dumps(data))
        self.assert200(resp)
        resp = self.client.get('/review/%s' % review["id"]).json
        self.assertEqual(resp['review']['text'], data['text'])
        self.assertEqual(resp['review']['rating'], review['rating'])

    def test_review_list(self):
        review = self.create_dummy_review()
        resp = self.client.get('/review/').json
        self.assertEqual(resp['count'], 1)
        self.assertEqual(len(resp['reviews']), 1)
        self.assertEqual(resp['reviews'][0]['id'], str(review['id']))
        # TODO(roman): Completely verify output (I encountered unicode issues when tried to do that).

    def test_review_post(self):
        review = dict(
            entity_id=self.review['entity_id'],
            entity_type='release_group',
            text=self.review['text'],
            rating=str(self.review['rating']),
            license_choice=self.license["id"],
            language='en',
            is_draft=True
        )
        resp = self.client.post('/review/', headers=self.header(self.user), data=json.dumps(review))
        self.assert200(resp)

        review_2 = dict(
            entity_id=self.review['entity_id'],
            entity_type='release_group',
            license_choice=self.license["id"],
            language='en',
            is_draft=True
        )
        resp = self.client.post('/review/', headers=self.header(self.another_user), data=json.dumps(review_2))
        self.assert400(resp, "Review must have either text or rating")

        # test writing a normal review works using the API. this test may not look useful but interestingly,
        # writing a review using the API was broken for at least a year and no one seemed to notice or report
        # it. so here it is, a test to write a valid review using the API.
        review_3 = dict(
            entity_id=self.review['entity_id'],
            entity_type='release_group',
            license_choice=self.license["id"],
            language='en',
            text="Hello, World! Let's write a long long long even longer the longest review........................"
        )
        resp = self.client.post('/review/', headers=self.header(self.another_user), data=json.dumps(review_3))
        self.assert200(resp)

    def test_review_vote_entity(self):
        review = self.create_dummy_review()
        resp = self.client.get('/review/%s/vote' % review["id"], headers=self.header(self.user))
        self.assert404(resp)

    def test_review_vote_put(self):
        review = self.create_dummy_review()

        resp = self.client.put(
            '/review/%s/vote' % review["id"],
            headers=self.header(self.user),
            data=json.dumps({"vote": True})
        )
        self.assertEqual(resp.json['description'], 'You cannot rate your own review.')

        resp = self.client.put(
            '/review/%s/vote' % review["id"],
            headers=self.header(self.another_user),
            data=json.dumps({"vote": True})
        )
        self.assert200(resp)

        resp = self.client.put(
            '/review/%s/vote' % review["id"],
            headers=self.header(self.another_user),
            data=json.dumps({"vote": False})
        )
        self.assert200(resp)

        # Update to review to only-rating type
        db_review.update(
            review_id=review["id"],
            drafted=review["is_draft"],
            rating=5,
            is_draft=False,
        )
        resp = self.client.put(
            '/review/%s/vote' % review["id"],
            headers=self.header(self.another_user),
            data=json.dumps({"vote": True})
        )
        self.assert400(resp, "Voting on reviews without text is not allowed.")

    def test_review_vote_delete(self):
        review = self.create_dummy_review()

        resp = self.client.delete('/review/%s/vote' % review["id"], headers=self.header(self.another_user))
        self.assert400(resp)

        vote = dict(vote=True)
        self.client.put('/review/%s/vote' % review["id"], headers=self.header(self.another_user), data=json.dumps(vote))
        resp = self.client.delete('/review/%s/vote' % review["id"], headers=self.header(self.another_user))
        self.assert200(resp)

    def test_revision_entity_handler(self):
        review = self.create_dummy_review()
        resp = self.client.get('/review/%s/revisions/1' % review["id"])
        self.assert200(resp)
        data = dict(text="This is an updated review")
        self.client.post('/review/%s' % review["id"], headers=self.header(self.user), data=json.dumps(data))
        resp = self.client.get('/review/%s/revisions/2' % review["id"])
        self.assert200(resp)
