import json

from critiquebrainz.ws.testing import WebServiceTestCase
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.license import License


class ReviewViewsTestCase(WebServiceTestCase):

    def setUp(self):
        super(ReviewViewsTestCase, self).setUp()
        self.user = User.get_or_create("Tester", "aef06569-098f-4218-a577-b413944d9493")
        self.another_user = User.get_or_create("Hacker!", "9371e5c7-5995-4471-a5a9-33481f897f9c")
        self.license = License.create("CC BY-SA 3.0", "Created so we can fill the form correctly.")
        self.review = dict(
            entity_id="6b3cd75d-7453-39f3-86c4-1441f360e121",
            entity_type='release_group',
            user=self.user,
            text="Testing! This text should be on the page.",
            is_draft=False,
            license_id=self.license.id,
        )

    def header(self, user):
        data = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.create_dummy_token(user)
        }
        return data

    def create_dummy_review(self):
        return Review.create(**self.review)

    def test_review_count(self):
        resp = self.client.get('/review/').json
        self.assertEqual(resp['count'], 0)

    def test_review_entity(self):
        review = self.create_dummy_review()
        resp = self.client.get('/review/%s' % review.id).json
        self.assertEqual(resp['review']['id'], review.id)

    def test_review_delete(self):
        review = self.create_dummy_review()
        resp = self.client.delete('/review/%s' % review.id, headers=self.header(self.user))
        self.assert200(resp)

    def test_review_modify(self):
        review = self.create_dummy_review()

        resp = self.client.post('/review/%s' % review.id, headers=self.header(self.another_user))
        self.assert403(resp, "Shouldn't be able to edit someone else's review.")

        data = dict(text="Some updated text with length more than twenty five.")
        resp = self.client.post('/review/%s' % review.id, headers=self.header(self.user), data=json.dumps(data))
        self.assert200(resp)

    def test_review_list(self):
        review = self.create_dummy_review()
        resp = self.client.get('/review/').json
        self.assertEqual(resp['count'], 1)
        self.assertEqual(len(resp['reviews']), 1)
        self.assertEqual(resp['reviews'][0]['id'], review.id)
        # TODO(roman): Completely verify output (I encountered unicode issues when tried to do that).

    def test_review_post(self):
        review = dict(
            entity_id=self.review['entity_id'],
            entity_type='release_group',
            text=self.review['text'],
            license_choice=self.license.id,
            language='en',
            is_draft=True
        )

        resp = self.client.post('/review/', headers=self.header(self.user), data=json.dumps(review))
        self.assert200(resp)

    def test_review_vote_entity(self):
        review = self.create_dummy_review()
        resp = self.client.get('/review/%s/vote' % review.id, headers=self.header(self.user))
        self.assert404(resp)

    def test_review_vote_put(self):
        review = self.create_dummy_review()

        resp = self.client.put(
            '/review/%s/vote' % review.id,
            headers=self.header(self.user),
            data=json.dumps({"vote": True})
        )
        self.assertEqual(resp.json['description'], 'You cannot rate your own review.')

        resp = self.client.put(
            '/review/%s/vote' % review.id,
            headers=self.header(self.another_user),
            data=json.dumps({"vote": True})
        )
        self.assert200(resp)

        resp = self.client.put(
            '/review/%s/vote' % review.id,
            headers=self.header(self.another_user),
            data=json.dumps({"vote": False})
        )
        self.assert200(resp)

    def test_review_vote_delete(self):
        review = self.create_dummy_review()

        resp = self.client.delete('/review/%s/vote' % review.id, headers=self.header(self.another_user))
        self.assert400(resp)

        vote = dict(vote=True)
        self.client.put('/review/%s/vote' % review.id, headers=self.header(self.another_user), data=json.dumps(vote))
        resp = self.client.delete('/review/%s/vote' % review.id, headers=self.header(self.another_user))
        self.assert200(resp)
