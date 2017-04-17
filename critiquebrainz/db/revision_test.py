from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import db
import critiquebrainz.db.review as db_review
from critiquebrainz.data.model.user import User
from critiquebrainz.db import revision
from critiquebrainz.db import vote
from datetime import datetime
import critiquebrainz.db.license as db_license


class RevisionTestCase(DataTestCase):

    def setUp(self):
        super(RevisionTestCase, self).setUp()
        self.author = User.get_or_create('Author', musicbrainz_id='0')
        self.user_1 = User.get_or_create('Tester #1', musicbrainz_id='1')
        self.user_2 = User.get_or_create('Tester #2', musicbrainz_id='2')
        self.license = db_license.create(
            id=u'TEST',
            full_name=u"Test License",
        )
        self.review = db_review.create(
            user_id=self.author.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text=u"Testing!",
            is_draft=False,
            license_id=self.license["id"],
        )

    def test_get_and_count(self):
        """Test the get function that gets revisions for the test review ordered by the timestamp
        and the count function that returns the total number of revisions of a review"""

        review_id = self.review["id"]
        count = revision.get_count(review_id)
        first_revision = revision.get(review_id)[0]
        self.assertEqual(count, 1)
        self.assertEqual(first_revision['text'], "Testing!")
        self.assertEqual(type(first_revision['timestamp']), datetime)
        self.assertEqual(type(first_revision['id']), int)

        db_review.update(
            review_id=self.review["id"],
            drafted=self.review["is_draft"],
            text="Testing Again!",
        )
        second_revision = revision.get(review_id)[0]
        count = revision.get_count(review_id)
        self.assertEqual(count, 2)
        self.assertEqual(second_revision['text'], "Testing Again!")
        self.assertEqual(type(second_revision['timestamp']), datetime)
        self.assertEqual(type(second_revision['id']), int)

        db_review.update(
            review_id=self.review["id"],
            drafted=self.review["is_draft"],
            text="Testing Once Again!",
        )
        # Testing offset and limit
        first_two_revisions = revision.get(review_id, limit=2, offset=1)
        count = revision.get_count(review_id)
        self.assertEqual(count, 3)
        self.assertEqual(first_two_revisions[1]['text'], "Testing!")
        self.assertEqual(first_two_revisions[0]['text'], "Testing Again!")

    def test_get_all_votes(self):
        """Test to get the number of votes on revisions of a review"""

        review_id = self.review["id"]
        count = revision.get_count(review_id)
        first_revision = revision.get(review_id)[0]
        vote.submit(self.user_1.id, first_revision['id'], True)
        vote.submit(self.user_2.id, first_revision['id'], False)
        votes = revision.get_all_votes(review_id)
        votes_first_revision = votes[first_revision['id']]
        self.assertDictEqual(votes_first_revision, {
            "positive":1,
            "negative":1
        })

    def test_get_revision_number(self):
        """Test to get the revision number of a revision of a specified review."""
        rev_num = revision.get_revision_number(self.review["id"], self.review["last_revision"]["id"])
        self.assertEqual(rev_num, 1)
        db_review.update(
            review_id=self.review["id"],
            drafted=self.review["is_draft"],
            text="Updated this review",
        )
        self.review = db_review.get_by_id(self.review["id"])
        rev_num = revision.get_revision_number(self.review["id"], self.review["last_revision"]["id"])
        self.assertEqual(rev_num, 2)
