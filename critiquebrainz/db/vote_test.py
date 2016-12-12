from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data import db
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.license import License
from critiquebrainz.db import exceptions
from critiquebrainz.db import vote
from datetime import datetime
from uuid import UUID


class VoteTestCase(DataTestCase):

    def setUp(self):
        super(VoteTestCase, self).setUp()
        author = User.get_or_create('Author', musicbrainz_id='0')
        self.user_1 = User.get_or_create('Tester #1', musicbrainz_id='1')
        self.user_2 = User.get_or_create('Tester #2', musicbrainz_id='2')
        license = License(id='Test', full_name='Test License')
        db.session.add(license)
        db.session.commit()
        self.review = Review.create(release_group='e7aad618-fa86-3983-9e77-405e21796eca',
                               text="Testing!",
                               user=author,
                               is_draft=False,
                               license_id=license.id)

    def test_get_missing(self):
        with self.assertRaises(exceptions.NoDataFoundException):
            vote.get(self.user_1.id, self.review.last_revision.id)

    def test_get(self):
        vote_1 = Vote.create(self.user_1, self.review, True)
        vote_1_data = vote.get(self.user_1.id, self.review.last_revision.id)
        self.assertDictEqual(vote_1_data, {
                "user_id": UUID(vote_1.user_id),
                "revision_id": vote_1.revision_id,
                "vote": True,
                "rated_at": vote_1.rated_at
            })
        self.assertEqual(type(vote_1_data["user_id"]), UUID)
        self.assertEqual(type(vote_1_data["revision_id"]), int)
        self.assertEqual(type(vote_1_data["rated_at"]), datetime)

        vote_2 = Vote.create(self.user_2, self.review, False)
        vote_2_data = vote.get(self.user_2.id, self.review.last_revision.id)
        self.assertDictEqual(vote_2_data, {
            "user_id": UUID(vote_2.user_id),
            "revision_id": vote_2.revision_id,
            "vote": False,
            "rated_at": vote_2.rated_at
        })
