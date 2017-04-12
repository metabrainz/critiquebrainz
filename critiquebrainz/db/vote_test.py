from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data.model.vote import Vote
from critiquebrainz.db.user import User
import critiquebrainz.db.users as db_users
from critiquebrainz.data.model.review import Review
import critiquebrainz.db.license as db_license
from critiquebrainz.db import exceptions
from critiquebrainz.db import vote
from datetime import datetime
from uuid import UUID


class VoteTestCase(DataTestCase):

    def setUp(self):
        super(VoteTestCase, self).setUp()
        author = User(db_users.get_or_create('0', new_user_data={
            "display_name": "Author",
        }))
        self.user_1 = User(db_users.get_or_create('1', new_user_data={
            "display_name": "Tester #1",
        }))
        self.user_2 = User(db_users.get_or_create('2', new_user_data={
            "display_name": "Tester #2",
        }))
        license = db_license.create(
            id='Test',
            full_name='Test License'
        )
        self.review = Review.create(
            release_group='e7aad618-fa86-3983-9e77-405e21796eca',
            text="Testing!",
            user_id=author.id,
            is_draft=False,
            license_id=license["id"],
        )

    def test_get_missing(self):
        with self.assertRaises(exceptions.NoDataFoundException):
            vote.get(self.user_1.id, self.review.last_revision.id)

    def test_get(self):
        vote_1 = Vote.create(self.user_1.id, self.review, True)
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

        vote_2 = Vote.create(self.user_2.id, self.review, False)
        vote_2_data = vote.get(self.user_2.id, self.review.last_revision.id)
        self.assertDictEqual(vote_2_data, {
            "user_id": UUID(vote_2.user_id),
            "revision_id": vote_2.revision_id,
            "vote": False,
            "rated_at": vote_2.rated_at
        })
