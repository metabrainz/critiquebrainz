from datetime import datetime
from uuid import UUID
from critiquebrainz.data.testing import DataTestCase
import critiquebrainz.db.users as db_users
import critiquebrainz.db.review as db_review
import critiquebrainz.db.license as db_license
from critiquebrainz.db import exceptions
from critiquebrainz.db import vote
from critiquebrainz.db.user import User


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
            full_name='Test License',
        )
        self.review = db_review.create(
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Testing!",
            rating=5,
            user_id=author.id,
            is_draft=False,
            license_id=license["id"],
        )

    def test_get_missing(self):
        with self.assertRaises(exceptions.NoDataFoundException):
            vote.get(self.user_1.id, self.review["last_revision"]["id"])

    def test_get(self):
        vote.submit(self.user_1.id, self.review["last_revision"]["id"], True)
        vote_1_data = vote.get(self.user_1.id, self.review["last_revision"]["id"])
        rated_at = vote_1_data.pop("rated_at")
        self.assertDictEqual(vote_1_data, {
            "user_id": UUID(self.user_1.id),
            "revision_id": self.review["last_revision"]["id"],
            "vote": True,
        })
        self.assertEqual(type(vote_1_data["user_id"]), UUID)
        self.assertEqual(type(vote_1_data["revision_id"]), int)
        self.assertEqual(type(rated_at), datetime)

        vote.submit(self.user_2.id, self.review["last_revision"]["id"], False)
        vote_2_data = vote.get(self.user_2.id, self.review["last_revision"]["id"])
        vote_2_data.pop("rated_at")
        self.assertDictEqual(vote_2_data, {
            "user_id": UUID(self.user_2.id),
            "revision_id": self.review["last_revision"]["id"],
            "vote": False,
        })
