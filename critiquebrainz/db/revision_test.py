from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import db
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.license import License
from critiquebrainz.data.model.user import User
from critiquebrainz.db import revision
from critiquebrainz.db import vote
from datetime import datetime


class RevisionTestCase(DataTestCase):

    def setUp(self):
        super(RevisionTestCase, self).setUp()
        author = User.get_or_create('Author', musicbrainz_id='0')
        self.user_1 = User.get_or_create('Tester #1', musicbrainz_id='1')
        self.user_2 = User.get_or_create('Tester #2', musicbrainz_id='2')
        self.license = License(id=u'TEST', full_name=u"Test License")
        db.session.add(self.license)
        db.session.commit()

        self.review = Review.create(user=author,
                                    release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                                    text=u"Testing!",
                                    is_draft=False,
                                    license_id=self.license.id)

    def test_get(self):
        """Test the get function that gets revisions for the test review, optionally ordered by the timestamp"""

        review_id = self.review.id
        revisions, count = revision.get(review_id)
        first_revision = revisions[0]
        self.assertEqual(first_revision.text, "Testing!")
        self.assertEqual(type(first_revision.timestamp), datetime)
        self.assertEqual(type(first_revision.id), int)

        self.review.update(text="Testing Again!")
        # order by desc ensures that the second revision refers to the latest revision
        revisions, count = revision.get(review_id, order_desc=True)
        second_revision = revisions[0]
        self.assertEqual(second_revision.text, "Testing Again!")
        self.assertEqual(type(second_revision.timestamp), datetime)
        self.assertEqual(type(second_revision.id), int)


    def test_get_votes(self):
        """Test to get the number of votes on revisions of a review"""

        review_id = self.review.id
        revisions, count = revision.get(review_id)
        first_revision = revisions[0]
        vote.submit(self.user_1.id, first_revision.id, True)
        vote.submit(self.user_2.id, first_revision.id, False)
        votes = revision.get_votes(review_id)
        votes_first_revision = votes[first_revision.id]
        self.assertDictEqual(votes_first_revision, {
            "positive":1,
            "negative":1
        })
