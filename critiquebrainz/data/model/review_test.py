from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import db
from werkzeug.exceptions import BadRequest
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.license import License
from critiquebrainz.data.model.review import Review


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
        self.assertEqual(Review.query.count(), 0)

        review = Review.create(user=self.user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=u"Testing!",
                               is_draft=False,
                               license_id=self.license.id)

        reviews = Review.query.all()
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0].id, review.id)
        self.assertEqual(reviews[0].entity_id, review.entity_id)
        self.assertEqual(reviews[0].license_id, review.license_id)

    def test_created_property(self):
        review = Review.create(user=self.user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=u"Testing!",
                               is_draft=False,
                               license_id=self.license.id)
        self.assertEqual(review.created, review.revisions[0].timestamp)

    def test_review_deletion(self):
        review = Review.create(user=self.user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=u"Testing!",
                               is_draft=False,
                               license_id=self.license.id)
        self.assertEqual(Review.query.count(), 1)

        review.delete()
        self.assertEqual(Review.query.count(), 0)

    def test_languages(self):
        review_en = Review.create(user=self.user,
                                  release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                                  text=u"Testing!",
                                  is_draft=False,
                                  license_id=self.license.id,
                                  language='en')
        review_de = Review.create(user=self.user,
                                  release_group='e7aad618-fa86-3983-9e77-405e21796ece',
                                  text=u"Testing!",
                                  is_draft=False,
                                  license_id=self.license.id,
                                  language='de')

        reviews, count = Review.list(language='de')
        self.assertEqual(len(reviews), 1)
        self.assertEqual(count, 1)

        reviews, count = Review.list(language='ru')
        self.assertEqual(len(reviews), 0)
        self.assertEqual(count, 0)

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
        self.assertEqual(len(retrieved_review.revisions), 2)
        self.assertNotEqual(retrieved_review.revisions[0], retrieved_review.last_revision)

        # Let's try doing some things that shouldn't be allowed!

        with self.assertRaises(BadRequest):  # like changing license...
            review.update(text=u"Sucks!", license_id=self.license.id)

        with self.assertRaises(BadRequest):  # or converting review back to draft...
            review.update(text=u"Sucks!", is_draft=True)

    def test_revisions(self):
        review = Review.create(user=self.user,
                               release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text=u"Awesome!",
                               is_draft=False,
                               license_id=self.license.id)
        self.assertEqual(len(review.revisions), 1)
        self.assertEqual(review.revisions[0], review.last_revision)

        # Updating should create a new revision.
        review.update(text=u"The worst!")
        self.assertEqual(len(review.revisions), 2)
        self.assertNotEqual(review.revisions[0], review.last_revision)

    def test_list(self):
        reviews, count = Review.list()
        self.assertEqual(count, 0)
        self.assertEqual(len(reviews), 0)

        review = Review.create(
            user=self.user,
            release_group='e7aad618-fa86-3983-9e77-405e21796eca',
            text=u"Awesome!",
            is_draft=False,
            license_id=self.license.id
        )
        reviews, count = Review.list()
        self.assertEqual(count, 1)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0].text, u"Awesome!")

        review.update(
            text=u"Beautiful!",
        )
        reviews, count = Review.list()
        self.assertEqual(count, 1)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0].text, u"Beautiful!")

        reviews, count = Review.list(sort='rating')
        self.assertEqual(count, 1)
        self.assertEqual(len(reviews), 1)

        reviews, count = Review.list(sort='created')
        self.assertEqual(count, 1)
        self.assertEqual(len(reviews), 1)

    def test_get_popular(self):
        reviews = Review.get_popular()
        self.assertEqual(len(reviews), 0)

        new_review = Review.create(
            user=self.user,
            release_group='e7aad618-fa86-3983-9e77-405e21796eca',
            text=u"Testing!",
            is_draft=False,
            license_id=self.license.id
        )

        reviews = Review.get_popular()
        self.assertEqual(len(reviews), 1)
