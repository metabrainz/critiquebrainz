from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import db
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from werkzeug.exceptions import BadRequest
from critiquebrainz.data.model.license import License
import critiquebrainz.db.review as db_review
import critiquebrainz.db.revision as db_revision

class ReviewTestCase(DataTestCase):

    def setUp(self):
        super(ReviewTestCase, self).setUp()

        # Review needs user
        self.user = User(db_users.get_or_create("Tester", new_user_data={
            "display_name": "test user",
        }))
        # And license
        self.license = License(id=u"Test", full_name="Test License")
        db.session.add(self.license)
        db.session.commit()

    def test_review_creation(self):
        review = db_review.create(
           user_id=self.user.id,
           release_group="e7aad618-fa86-3983-9e77-405e21796eca",
           text="Testing",
           is_draft=False,
           license_id=self.license.id,
        )
        reviews, count = db_review.list_reviews()
        self.assertEqual(count, 1)
        self.assertEqual(reviews[0]["id"], review["id"])
        self.assertEqual(reviews[0]["entity_id"], review["entity_id"])
        self.assertEqual(reviews[0]["license_id"], review["license_id"])

    def test_review_deletion(self):
        review = db_review.create(
            user_id=self.user.id,
            release_group="e7aad618-fa86-3983-9e77-405e21796eca",
            text="Testing",
            is_draft=False,
            license_id=self.license.id,
        )
        self.assertEqual(db_review.list_reviews()[1], 1)
        db_review.delete(review["id"])
        self.assertEqual(db_review.list_reviews()[1], 0)

    def test_languages(self):
        review_en = db_review.create(
            user_id=self.user.id,
            release_group="e7aad618-fa86-3983-9e77-405e21796ece",
            text="Testing",
            is_draft=False,
            license_id=self.license.id,
            language="en",
        )

        review_de = db_review.create(
            user_id=self.user.id,
            release_group="e7aad618-fa86-3983-9e77-405e21796eca",
            text="Testing",
            is_draft=False,
            license_id=self.license.id,
            language="de",
        )
        reviews, count = db_review.list_reviews(language="de")
        self.assertEqual(len(reviews), 1)
        self.assertEqual(count, 1)

        reviews, count = db_review.list_reviews(language="ru")
        self.assertEqual(count, 0)

    def test_update(self):
        review = db_review.create(
            user_id=self.user.id,
            release_group="e7aad618-fa86-3983-9e77-405e21796eca",
            text="Testing",
            is_draft=True,
            license_id=self.license.id,
        )
        another_license = License(id="License-2", full_name="Another License")
        db.session.add(another_license)
        db.session.commit()
        review = db_review.update(
            review_id=review["id"],
            drafted=review["is_draft"],
            text="Bad update",
            is_draft=False,
            license_id=another_license.id,
            language="es",
        )
        # Checking if contents are updated
        retrieved_review = db_review.list_reviews()[0][0]
        self.assertEqual(retrieved_review["text"], "Bad update")
        self.assertFalse(retrieved_review["is_draft"])
        self.assertEqual(retrieved_review["license_id"], another_license.id)
        self.assertEqual(retrieved_review["language"], "es")

        # Updating should create a new revision.
        revisions = db_revision.get(retrieved_review["id"], limit=None)
        self.assertEqual(len(revisions), 2)
        self.assertEqual(revisions[0], retrieved_review["last_revision"])

        # Checking things that shouldn't be allowed
        with self.assertRaises(BadRequest):
            review = db_review.update(
                review_id=review["id"],
                drafted=review["is_draft"],
                text="Sucks!",
                license_id=self.license.id,
            )

        with self.assertRaises(BadRequest):
            review = db_review.update(
                review_id=review["id"],
                drafted=review["is_draft"],
                text="Sucks!",
                is_draft=True,
            )

    def test_list_reviews(self):
        reviews, count = db_review.list_reviews()
        self.assertEqual(count, 0)
        self.assertEqual(len(reviews), 0)

        review = db_review.create(
            user_id=self.user.id,
            release_group="e7aad618-fa86-3983-9e77-405e21796eca",
            text="Awesome",
            is_draft=False,
            license_id=self.license.id,
        )
        reviews, count = db_review.list_reviews()
        self.assertEqual(count, 1)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]["text"], "Awesome")

        review = db_review.update(
            review_id=review["id"],
            drafted=review["is_draft"],
            text="Beautiful!",
        )
        reviews, count = db_review.list_reviews()
        self.assertEqual(count, 1)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]["text"], "Beautiful!")

        reviews, count = db_review.list_reviews(sort="rating")
        self.assertEqual(count, 1)
        self.assertEqual(len(reviews), 1)

        reviews, count = db_review.list_reviews(sort="created")
        self.assertEqual(count, 1)
        self.assertEqual(len(reviews), 1)

        reviews, count = db_review.list_reviews(sort="random")
        self.assertEqual(count, 1)
        self.assertEqual(len(reviews), 1)

    def test_get_popular(self):
        reviews = db_review.get_popular()
        self.assertEqual(len(reviews), 0)

        new_review = db_review.create(
            user_id=self.user.id,
            release_group="e7aad618-fa86-3983-9e77-405e21796eca",
            text="Awesome",
            is_draft=False,
            license_id=self.license.id,
        )

        reviews = db_review.get_popular()
        self.assertEqual(len(reviews), 1)

    def test_hide_and_unhide(self):
        review = db_review.create(
            user_id=self.user.id,
            release_group="e7aad618-fa86-3983-9e77-405e21796eca",
            text="Awesome",
            is_draft=False,
            license_id=self.license.id,
        )
        db_review.hide(review["id"])
        review = db_review.get_by_id(review["id"])
        self.assertEqual(review["is_hidden"], True)
        db_review.unhide(review["id"])
        review = db_review.get_by_id(review["id"])
        self.assertEqual(review["is_hidden"], False)

    def test_get_count(self):
        count = db_review.get_count()
        self.assertEqual(count, 0)
        review = db_review.create(
            user_id=self.user.id,
            release_group="e7aad618-fa86-3983-9e77-405e21796eca",
            text="Awesome",
            is_draft=False,
            license_id=self.license.id,
        )
        count = db_review.get_count(is_draft=False, is_hidden=False)
        self.assertEqual(count, 1)
