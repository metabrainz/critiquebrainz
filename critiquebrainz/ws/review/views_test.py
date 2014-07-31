from critiquebrainz.testing import ServerTestCase
from critiquebrainz.data import db
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.license import License
import json


class ReviewViewsTestCase(ServerTestCase):

    def test_review_count(self):
        resp = self.client.get('/ws/1/review/')
        data = json.loads(resp.data)
        assert data['count'] == 0

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
                               license_id=license.id)

        resp = self.client.get('/ws/1/review/')
        data = json.loads(resp.data)

        assert data['count'] == 1
        assert len(data['reviews']) == 1
        stored_review = data['reviews'][0]
        assert stored_review['id'] == review.id
        assert stored_review['release_group'] == review.release_group
        assert stored_review['text'] == text
        assert stored_review['license']['id'] == license.id
        assert stored_review['license']['full_name'] == license.full_name
