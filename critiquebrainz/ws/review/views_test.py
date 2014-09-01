from critiquebrainz.ws.testing import WebServiceTestCase
from critiquebrainz.data import db
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.license import License


class ReviewViewsTestCase(WebServiceTestCase):

    def test_review_count(self):
        resp = self.client.get('/review/').json
        self.assertEqual(resp['count'], 0)

    def test_review_creation(self):
        # Preparing test data
        user = User.get_or_create(u'Tester', musicbrainz_id=u'1')
        license = License(id=u'Test', full_name=u'Test License')
        db.session.add(license)
        db.session.commit()

        text = u"Testing!"
        review = Review.create(user=user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=text,
                               is_draft=False,
                               license_id=license.id)

        resp = self.client.get('/review/').json
        self.assertEqual(resp['count'], 1)
        self.assertEqual(len(resp['reviews']), 1)
        self.assertEqual(resp['reviews'][0]['id'], review.id)
        # TODO: Completely verify output (I encountered unicode issues when tried to do that).
