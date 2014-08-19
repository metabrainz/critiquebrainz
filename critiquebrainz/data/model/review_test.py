from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import db
from critiquebrainz.frontend.exceptions import InvalidRequest
from user import User
from license import License
from review import Review


class ReviewTestCase(DataTestCase):

    def setUp(self):
        super(ReviewTestCase, self).setUp()

        # Review needs user
        self.user = User(display_name=u'Tester')
        db.session.add(self.user)
        db.session.commit()

        # and license
        self.license = License(id=u"Test", full_name=u'Test License')
        db.session.add(self.license)
        db.session.commit()

    def test_review_creation(self):
        assert Review.query.count() == 0

        review = Review.create(user=self.user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=u"Testing!",
                               license_id=self.license.id)

        reviews = Review.query.all()
        assert len(reviews) == 1
        assert reviews[0].id == review.id
        assert reviews[0].release_group == review.release_group
        assert reviews[0].license_id == review.license_id

    def test_created_property(self):
        review = Review.create(user=self.user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=u"Testing!",
                               is_draft=False,
                               license_id=self.license.id)
        self.assertEqual(review.created, review.first_revision.timestamp)

    def test_review_deletion(self):
        review = Review.create(user=self.user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=u"Testing!",
                               is_draft=False,
                               license_id=self.license.id)
        assert Review.query.count() == 1

        review.delete()
        assert Review.query.count() == 0

    def test_languages(self):
        review_en = Review.create(user=self.user,
                                  release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                                  text=u"Testing!",
                                  license_id=self.license.id,
                                  language='en')
        review_de = Review.create(user=self.user,
                                  release_group='e7aad618-fa86-3983-9e77-405e21796ece',
                                  text=u"Testing!",
                                  license_id=self.license.id,
                                  language='de')

        reviews, count = Review.list(language='de')
        assert len(reviews) == 1 and count == 1

    def test_update(self):
        review = Review.create(user=self.user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=u"Awesome!",
                               is_draft=True,
                               license_id=self.license.id)
        another_license = License(id=u"License-2", full_name=u"Another license")
        db.session.add(another_license)
        db.session.commit()
        review.update(text=u"Bad...", is_draft=False, license_id=another_license.id, language='es')

        # Checking if contents are updated
        retrieved_review = Review.query.all()[0]
        self.assertEqual(retrieved_review.text, u"Bad...")
        self.assertFalse(retrieved_review.is_draft)
        self.assertEqual(retrieved_review.license_id, another_license.id)
        self.assertEqual(retrieved_review.language, 'es')

        # Updating should create a new revision.
        assert len(retrieved_review.revisions) == 2
        self.assertNotEqual(retrieved_review.first_revision, retrieved_review.last_revision)

        # Let's try doing some things that shouldn't be allowed!

        with self.assertRaises(InvalidRequest):  # like changing license...
            review.update(text=u"Sucks!", license_id=self.license.id)

        with self.assertRaises(InvalidRequest):  # or converting review back to draft...
            review.update(text=u"Sucks!", is_draft=True)

    def test_revisions(self):
        review = Review.create(user=self.user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=u"Awesome!",
                               is_draft=False,
                               license_id=self.license.id)
        assert len(review.revisions) == 1
        self.assertEqual(review.first_revision, review.last_revision)

        # Updating should create a new revision.
        review.update(u"The worst!")
        assert len(review.revisions) == 2
        self.assertNotEqual(review.first_revision, review.last_revision)
