# critiquebrainz - Repository for Creative Commons licensed reviews
#
# Copyright (C) 2019 Bimalkant Lauhny.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from unittest.mock import MagicMock
from brainzutils import cache
from critiquebrainz.data.testing import DataTestCase
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
import critiquebrainz.db.review as db_review
import critiquebrainz.db.vote as db_vote
import critiquebrainz.db.comment as db_comment
import critiquebrainz.db.license as db_license
import critiquebrainz.db.statistics as db_statistics


class StatisticsTestCase(DataTestCase):

    def setUp(self):
        super(StatisticsTestCase, self).setUp()

        self.user_1 = User(db_users.get_or_create(1, "Tester 1", new_user_data={
            "display_name": "test user 1",
        }))
        self.user_2 = User(db_users.get_or_create(2, "Tester 2", new_user_data={
            "display_name": "test user 2",
        }))

        self.license = db_license.create(
            id=u'Test',
            full_name=u"Test License",
        )

        # totally disable cache get or set
        cache.gen_key = MagicMock(return_value=None)
        cache.get = MagicMock(return_value=None)
        cache.set = MagicMock(return_value=None)

    def create_dummy_review(self, user_id):
        return db_review.create(
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text=u"Test review",
            rating=5,
            user_id=user_id,
            is_draft=False,
            license_id=self.license["id"],
        )

    def test_get_users_with_review_count(self):
        # user_1 added a review
        self.create_dummy_review(user_id=self.user_1.id)

        # get list of users with review_count
        users_review_count = db_statistics.get_users_with_review_count()
        print("User Reviews: ", users_review_count)
        for user in users_review_count:
            if str(user["id"]) == self.user_1.id:
                self.assertEqual(user["review_count"], 1)
            else:
                self.assertEqual(user["review_count"], 0)

    def test_get_users_with_comment_count(self):
        # user_1 added a review
        review_1 = self.create_dummy_review(user_id=self.user_1.id)

        # user_2 commented on review by user_1
        db_comment.create(
            user_id=self.user_2.id,
            review_id=review_1["id"],
            text="Test comment",
        )

        # get list of users with comment_count
        users_comment_count = db_statistics.get_users_with_comment_count()
        print("User Comments: ", users_comment_count)
        for user in users_comment_count:
            if str(user["id"]) == self.user_2.id:
                self.assertEqual(user["comment_count"], 1)
            else:
                self.assertEqual(user["comment_count"], 0)

    def test_get_users_with_vote_count(self):
        # user_2 added a review
        review_2 = self.create_dummy_review(user_id=self.user_2.id)

        # user_1 upvoted review by user_2
        db_vote.submit(
            user_id=self.user_1.id,
            revision_id=review_2["last_revision"]["id"],
            vote=True,
        )

        # get list of users with comment_count
        users_vote_count = db_statistics.get_users_with_vote_count()
        print("User Votes: ", users_vote_count)
        for user in users_vote_count:
            if str(user["id"]) == self.user_1.id:
                self.assertEqual(user["vote_count"], 1)
            else:
                self.assertEqual(user["vote_count"], 0)

    def test_get_top_users(self):

        # user_1 added a review
        review_1 = self.create_dummy_review(user_id=self.user_1.id)

        # get list of top users
        top_users = db_statistics.get_top_users()
        self.assertEqual(len(top_users), 2)
        self.assertEqual(top_users[0]["id"], self.user_1.id)
        self.assertEqual(top_users[0]["score"], 1)

        # user_2 added a review
        self.create_dummy_review(user_id=self.user_2.id)

        # user_2 commented on review by user_1
        db_comment.create(
            user_id=self.user_2.id,
            review_id=review_1["id"],
            text="Test comment",
        )

        # get list of top users
        top_users = db_statistics.get_top_users()
        self.assertEqual(top_users[0]["id"], self.user_2.id)
        self.assertEqual(top_users[0]["score"], 2)
        self.assertEqual(top_users[1]["id"], self.user_1.id)
        self.assertEqual(top_users[1]["score"], 1)

    def test_get_top_users_overall(self):
        # user_1 added a review
        review_1 = self.create_dummy_review(user_id=self.user_1.id)

        # user_2 added a review
        review_2 = self.create_dummy_review(user_id=self.user_2.id)

        # user_2 commented on review by user_1
        db_comment.create(
            user_id=self.user_2.id,
            review_id=review_1["id"],
            text="Test comment",
        )

        # user_1 upvoted review by user_2
        db_vote.submit(
            user_id=self.user_1.id,
            revision_id=review_2["last_revision"]["id"],
            vote=True,
        )

        # get list of top users
        top_users = db_statistics.get_top_users_overall()
        self.assertEqual(len(top_users), 2)
        self.assertEqual(top_users[0]["id"], self.user_2.id)
        self.assertEqual(top_users[0]["score"], 7)
        self.assertEqual(top_users[1]["id"], self.user_1.id)
        self.assertEqual(top_users[1]["score"], 6)
