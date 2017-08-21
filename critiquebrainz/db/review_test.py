from critiquebrainz.data.testing import DataTestCase
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
import critiquebrainz.db.review as db_review
import critiquebrainz.db.revision as db_revision
import critiquebrainz.db.exceptions as db_exceptions
import critiquebrainz.db.license as db_license


class ReviewTestCase(DataTestCase):

    def setUp(self):
        super(ReviewTestCase, self).setUp()

        # Review needs user
        self.user = User(db_users.get_or_create("Tester", new_user_data={
            "display_name": "test user",
        }))
        self.user_2 = User(db_users.get_or_create("Tester 2", new_user_data={
            "display_name": "test user 2",
        }))

        # And license
        self.license = db_license.create(
            id=u'Test',
            full_name=u"Test License",
        )

    def test_review_creation(self):
        review = db_review.create(
            user_id=self.user.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Testing",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )
        reviews, count = db_review.list_reviews()
        self.assertEqual(count, 1)
        self.assertEqual(reviews[0]["id"], review["id"])
        self.assertEqual(reviews[0]["entity_id"], review["entity_id"])
        self.assertEqual(reviews[0]["license_id"], review["license_id"])
        self.assertEqual(reviews[0]["rating"], review["rating"])

        with self.assertRaises(db_exceptions.BadDataException):
            db_review.create(
                user_id=self.user_2.id,
                entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
                entity_type="release_group",
                is_draft=False,
                license_id=self.license["id"],
            )

    def test_review_deletion(self):
        review = db_review.create(
            user_id=self.user.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Testing",
            is_draft=False,
            license_id=self.license["id"],
        )
        self.assertEqual(db_review.list_reviews()[1], 1)
        db_review.delete(review["id"])
        self.assertEqual(db_review.list_reviews()[1], 0)

    def test_languages(self):
        db_review.create(
            user_id=self.user.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796ece",
            entity_type="release_group",
            text="Testing",
            is_draft=False,
            license_id=self.license["id"],
            language="en",
        )

        db_review.create(
            user_id=self.user.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Testing",
            is_draft=False,
            license_id=self.license["id"],
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
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Testing",
            rating=5,
            is_draft=True,
            license_id=self.license["id"],
        )
        another_license = db_license.create(
            id="License-2",
            full_name="Another License",
        )
        # Update review to only rating
        db_review.update(
            review_id=review["id"],
            drafted=review["is_draft"],
            rating=4,
            is_draft=False,
            license_id=another_license["id"],
            language="es",
        )
        # Checking if contents are updated
        retrieved_review = db_review.list_reviews()[0][0]
        self.assertEqual(retrieved_review["text"], None)
        self.assertEqual(retrieved_review["rating"], 4)
        self.assertFalse(retrieved_review["is_draft"])
        self.assertEqual(retrieved_review["license_id"], another_license["id"])
        self.assertEqual(retrieved_review["language"], "es")
        # Update review to only text
        db_review.update(
            review_id=review["id"],
            drafted=review["is_draft"],
            text="Testing update",
            is_draft=False,
            license_id=another_license["id"],
            language="es",
        )
        # Checking if contents are updated
        retrieved_review = db_review.list_reviews()[0][0]
        self.assertEqual(retrieved_review["text"], "Testing update")
        self.assertEqual(retrieved_review["rating"], None)

        # Updating should create a new revision.
        revisions = db_revision.get(retrieved_review["id"], limit=None)
        self.assertEqual(len(revisions), 3)
        self.assertEqual(revisions[0]["timestamp"], retrieved_review["last_revision"]["timestamp"])
        self.assertEqual(revisions[0]["text"], retrieved_review["text"])
        self.assertEqual(revisions[0]["rating"], retrieved_review["rating"])

        # Checking things that shouldn't be allowed
        with self.assertRaises(db_exceptions.BadDataException):
            db_review.update(
                review_id=retrieved_review["id"],
                drafted=retrieved_review["is_draft"],
                text="Sucks!",
                license_id=self.license["id"],
            )
        review = db_review.get_by_id(review["id"])
        with self.assertRaises(db_exceptions.BadDataException):
            db_review.update(
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
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Awesome",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )
        reviews, count = db_review.list_reviews()
        self.assertEqual(count, 1)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]["text"], "Awesome")
        self.assertEqual(reviews[0]["rating"], 5)

        db_review.update(
            review_id=review["id"],
            drafted=review["is_draft"],
            text="Beautiful!",
            rating=4,
        )
        reviews, count = db_review.list_reviews()
        self.assertEqual(count, 1)
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0]["text"], "Beautiful!")
        self.assertEqual(reviews[0]["rating"], 4)

        reviews, count = db_review.list_reviews(sort="popularity")
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

        db_review.create(
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            user_id=self.user.id,
            text="Awesome",
            is_draft=False,
            license_id=self.license["id"],
        )

        reviews = db_review.get_popular()
        self.assertEqual(len(reviews), 1)

    def test_set_hidden_state(self):
        review = db_review.create(
            user_id=self.user.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Awesome",
            is_draft=False,
            license_id=self.license["id"],
        )
        db_review.set_hidden_state(review["id"], is_hidden=True)
        review = db_review.get_by_id(review["id"])
        self.assertEqual(review["is_hidden"], True)
        db_review.set_hidden_state(review["id"], is_hidden=False)
        review = db_review.get_by_id(review["id"])
        self.assertEqual(review["is_hidden"], False)

    def test_get_count(self):
        count = db_review.get_count()
        self.assertEqual(count, 0)
        db_review.create(
            user_id=self.user.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )
        count = db_review.get_count(is_draft=False, is_hidden=False)
        self.assertEqual(count, 1)

    def test_distinct_entities(self):
        db_review.create(
            user_id=self.user.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Awesome",
            is_draft=False,
            license_id=self.license["id"],
        )
        db_review.create(
            user_id=self.user_2.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )
        entities = db_review.distinct_entities()
        self.assertEqual(len(entities), 1)
