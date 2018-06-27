from critiquebrainz.data.testing import DataTestCase
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
import critiquebrainz.db.review as db_review
import critiquebrainz.db.avg_rating as db_avg_rating
import critiquebrainz.db.exceptions as db_exceptions
import critiquebrainz.db.license as db_license


class AvgRatingTestCase(DataTestCase):

    def setUp(self):
        super(AvgRatingTestCase, self).setUp()

        self.user = User(db_users.get_or_create("Tester", new_user_data={
            "display_name": "test user",
        }))
        self.user_2 = User(db_users.get_or_create("Tester 2", new_user_data={
            "display_name": "test user 2",
        }))
        self.license = db_license.create(
            id=u'Test',
            full_name=u"Test License",
        )

    def test_insert_and_get(self):
        """Test if rating and count are inserted on creation of the first review with rating
        and the get function that returns a dict containing rating and count"""

        review = db_review.create(
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text=u"Testing!",
            rating=5,
            user_id=self.user.id,
            is_draft=False,
            license_id=self.license["id"],
        )
        avg_rating = db_avg_rating.get(review["entity_id"], review["entity_type"])
        self.assertEqual(avg_rating["entity_id"], review["entity_id"])
        self.assertEqual(avg_rating["entity_type"], review["entity_type"])
        self.assertEqual(avg_rating["rating"], 5.0)
        self.assertEqual(avg_rating["count"], 1)

    def test_update(self):
        """Test if rating and count are updated when review is updated or deleted"""

        review = db_review.create(
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text=u"Testing!",
            rating=5,
            user_id=self.user.id,
            is_draft=False,
            license_id=self.license["id"],
        )
        review_2 = db_review.create(
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text=u"Testing!",
            rating=4,
            user_id=self.user_2.id,
            is_draft=False,
            license_id=self.license["id"],
        )
        avg_rating = db_avg_rating.get(review["entity_id"], review["entity_type"])
        self.assertEqual(avg_rating["entity_id"], review["entity_id"])
        self.assertEqual(avg_rating["entity_type"], review["entity_type"])
        self.assertEqual(avg_rating["rating"], 4.5)
        self.assertEqual(avg_rating["count"], 2)

        db_review.update(
            review_id=review_2["id"],
            drafted=review_2["is_draft"],
            text=u"Testing rating update",
            rating=None,
        )
        # Check if avg_rating is updated after change in rating
        avg_rating = db_avg_rating.get(review["entity_id"], review["entity_type"])
        self.assertEqual(avg_rating["rating"], 5.0)
        self.assertEqual(avg_rating["count"], 1)

        # Check if avg_rating is updated after a review with rating is deleted
        db_review.delete(review["id"])
        with self.assertRaises(db_exceptions.NoDataFoundException):
            db_avg_rating.get(review["entity_id"], review["entity_type"])

    def test_delete(self):
        """Test delete function that deletes avg_rating given entity_id and entity_type"""

        review = db_review.create(
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text=u"Testing!",
            rating=5,
            user_id=self.user.id,
            is_draft=False,
            license_id=self.license["id"],
        )
        avg_rating = db_avg_rating.get(review["entity_id"], review["entity_type"])
        self.assertEqual(avg_rating["count"], 1)
        db_review.delete(review["id"])
        with self.assertRaises(db_exceptions.NoDataFoundException):
            db_avg_rating.get(review["entity_id"], review["entity_type"])
