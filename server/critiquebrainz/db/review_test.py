from flask.ext.testing import TestCase

from critiquebrainz import create_app
from critiquebrainz.db import db, User, License, Review
import test_config


class ReviewTestCase(TestCase):
    def create_app(self):
        return create_app(test_config)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_review_creation(self):
        # Review needs user
        user = User(display_name=u'Tester')
        db.session.add(user)
        db.session.commit()

        # and license
        license = License(id=u"Test", full_name=u'Test License')
        db.session.add(license)
        db.session.commit()

        # Creating new review
        text = u"Testing!"
        review = Review.create(user=user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=text,
                               license_id=license.id)
        db.session.add(review)
        db.session.commit()

        reviews, count = Review.list()
        assert len(reviews) and count == 1
        stored_review = reviews[0]
        assert stored_review.id == review.id
        assert stored_review.release_group == review.release_group
        assert stored_review.license_id == license.id
