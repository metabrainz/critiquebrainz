import json

from critiquebrainz.ws.testing import WebServiceTestCase
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.license import License


class ReviewViewsTestCase(WebServiceTestCase):

    def setUp(self):
        super(ReviewViewsTestCase, self).setUp()
        self.user = User.get_or_create(u"Tester", u"aef06569-098f-4218-a577-b413944d9493")
        self.hacker = User.get_or_create(u"Hacker!", u"9371e5c7-5995-4471-a5a9-33481f897f9c")
        self.license = License.create(u"CC BY-SA 3.0", u"Created so we can fill the form correctly.")
        self.review = dict(
            release_group="6b3cd75d-7453-39f3-86c4-1441f360e121",
            user=self.user,
            text="Testing! This text should be on the page.",
            is_draft=False,
            license_id=self.license.id,
        )

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
        header = {'Authorization': "Bearer " + self.create_dummy_token(self.user)}
        resp = self.client.delete('/review/%s' % review.id, headers=header).json
        self.assertEqual(resp['message'], 'Request processed successfully')

    def test_review_modify(self):
        review = self.create_dummy_review()

        header = {'Authorization': "Bearer " + self.create_dummy_token(self.hacker)}
        resp = self.client.post('/review/%s' % review.id, headers=header)
        self.assert403(resp, "Shouldn't be able to edit someone else's review.")

        header = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.create_dummy_token(self.user)
        }
        data = dict(text="Some updated text with length more than twenty five.")
        resp = self.client.post('/review/%s' % review.id, headers=header, data=json.dumps(data)).json
        self.assertEqual(resp['message'], 'Request processed successfully')

    def test_review_list(self):
        review = self.create_dummy_review()
        resp = self.client.get('/review/').json
        self.assertEqual(resp['count'], 1)
        self.assertEqual(len(resp['reviews']), 1)
        self.assertEqual(resp['reviews'][0]['id'], review.id)
        # TODO (roman): Completely verify output (I encountered unicode issues when tried to do that).

    def test_review_post(self):
        header = {
            'Content-Type': 'application/json',
            'Authorization': "Bearer " + self.create_dummy_token(self.user)
        }

        review = dict(
            release_group=self.review['release_group'],
            text=self.review['text'],
            license_choice=self.license.id,
            language='en',
            is_draft=True
        )

        resp = self.client.post('/review/', headers=header, data=json.dumps(review)).json
        self.assertEqual(resp['message'], 'Request processed successfully')
