from critiquebrainz.test_case import ServerTestCase
from .. import db
from user import User
from license import License
from review import Review


class ReviewTestCase(ServerTestCase):

    def setUp(self):
        db.create_all()

        # Review needs user
        self.user = User(display_name=u'Tester')
        db.session.add(self.user)
        db.session.commit()

        # and license
        self.license = License(id=u"Test", full_name=u'Test License')
        db.session.add(self.license)
        db.session.commit()

    def test_review_creation(self):
        text = u"Testing!"
        review = Review.create(user=self.user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=text,
                               license_id=self.license.id)
        db.session.add(review)
        db.session.commit()

        reviews, count = Review.list()
        assert len(reviews) == 1 and count == 1
        stored_review = reviews[0]
        assert stored_review.id == review.id
        assert stored_review.release_group == review.release_group
        assert stored_review.license_id == self.license.id

    def test_languages(self):
        text = u"Testing!"
        review_en = Review.create(user=self.user,
                                  release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                                  text=text,
                                  license_id=self.license.id,
                                  language='en')
        review_de = Review.create(user=self.user,
                                  release_group='e7aad618-fa86-3983-9e77-405e21796ece',
                                  text=text,
                                  license_id=self.license.id,
                                  language='de')
        db.session.add(review_en)
        db.session.add(review_de)
        db.session.commit()

        reviews, count = Review.list(language='de')
        assert len(reviews) == 1 and count == 1
