# critiquebrainz - Repository for Creative Commons licensed reviews
#
# Copyright (C) 2018 MetaBrainz Foundation Inc.
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


import critiquebrainz.db.comment as db_comment
import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users

from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.db.user import User


class CommentTestCase(DataTestCase):

    def setUp(self):
        super(CommentTestCase, self).setUp()

        # each comment requires a user and a review, so create a user and
        # review

        # create user
        self.user = User(db_users.get_or_create(1, "Tester", new_user_data={
            "display_name": "test user",
        }))
        self.user_2 = User(db_users.get_or_create(2, "Tester 2", new_user_data={
            "display_name": "test user 2",
        }))

        # need to create a license before creating a review
        self.license = db_license.create(
            id=u'Test',
            full_name=u"Test License",
        )
        self.review = db_review.create(
            user_id=self.user.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Testing",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )

    def test_create_comment(self):
        comment = db_comment.create(
            user_id=self.user.id,
            review_id=self.review['id'],
            text='This is a comment',
        )

        comments, _ = db_comment.list_comments(review_id=self.review['id'])
        self.assertEqual(len(comments), 1)
        self.assertEqual(comment['id'], comments[0]['id'])
        self.assertEqual(comment['review_id'], comments[0]['review_id'])

    def test_delete_comment(self):
        comment = db_comment.create(
            user_id=self.user.id,
            review_id=self.review['id'],
            text='this comment will be deleted',
        )

        comments, _ = db_comment.list_comments(review_id=self.review['id'])
        self.assertEqual(len(comments), 1)

        db_comment.delete(comment['id'])
        comments, _ = db_comment.list_comments(review_id=self.review['id'])
        self.assertEqual(len(comments), 0)

    def test_edit_comment(self):
        comment = db_comment.create(
            user_id=self.user.id,
            review_id=self.review['id'],
            text='this comment will be edited',
        )
        self.assertEqual(comment['edits'], 0)
        self.assertEqual(comment['last_revision']['text'], 'this comment will be edited')

        db_comment.update(
            comment_id=comment['id'],
            text='now edited',
        )
        comment = db_comment.get_by_id(comment['id'])
        self.assertEqual(comment['edits'], 1)
        self.assertEqual(comment['last_revision']['text'], 'now edited')

    def test_count_comment(self):
        db_comment.create(
            user_id=self.user.id,
            review_id=self.review['id'],
            text='I liked this review, but disagree with one of your points',
        )

        count = db_comment.count_comments(review_id=self.review['id'])
        self.assertEqual(count, 1)

        db_comment.create(
            user_id=self.user_2.id,
            review_id=self.review['id'],
            text='Okay, but I still think that this album could have better beats.',
        )
        count = db_comment.count_comments(review_id=self.review['id'])
        self.assertEqual(count, 2)
        count = db_comment.count_comments(review_id=self.review['id'], user_id=self.user.id)
        self.assertEqual(count, 1)
