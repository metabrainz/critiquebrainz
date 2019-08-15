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

from flask import current_app, url_for
from critiquebrainz.frontend.testing import FrontendTestCase
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
import critiquebrainz.db.comment as db_comment
import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review


def mock_get_entity_by_id(id, type='release_group'):
    # pylint: disable=unused-argument
    return {
        'id': 'e7aad618-fa86-3983-9e77-405e21796eca',
        'title': 'Test Entity',
    }


class CommentViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(CommentViewsTestCase, self).setUp()
        self.reviewer = User(db_users.get_or_create(1, "aef06569-098f-4218-a577-b413944d9493", new_user_data={
            "display_name": u"Reviewer",
        }))
        self.commenter = User(db_users.get_or_create(2, "9371e5c7-5995-4471-a5a9-33481f897f9c", new_user_data={
            "display_name": u"Commenter",
        }))
        self.license = db_license.create(
            id="CC BY-SA 3.0",
            full_name="Test License.",
        )
        self.review = db_review.create(
            user_id=self.reviewer.id,
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Test Review.",
            rating=5,
            is_draft=False,
            license_id=self.license["id"],
        )
        current_app.jinja_env.filters["entity_details"] = mock_get_entity_by_id

    def create_dummy_comment(self):
        return db_comment.create(
            user_id=self.commenter.id,
            text="Dummy Comment",
            review_id=self.review["id"],
        )

    def test_create(self):
        self.temporary_login(self.commenter)

        comment_count = db_comment.count_comments(review_id=self.review["id"])
        # empty comment should be rejected
        payload = {
            "review_id": self.review["id"],
            "text": "",
            "state": "publish",
        }
        response = self.client.post(
            url_for("comment.create"),
            data=payload,
        )
        self.assertRedirects(response, url_for("review.entity", id=self.review["id"]))
        self.assertEqual(comment_count, db_comment.count_comments(review_id=self.review["id"]))
        response = self.client.get(url_for("review.entity", id=self.review["id"]))
        self.assert200(response)
        # Test that the rendered html should contain error message
        self.assertIn("Comment must not be empty!", str(response.data))

        # add some text to comment
        payload["text"] = "Test Comment."

        # get a 404 if review_id doesn't exist
        payload["review_id"] = "1bee4a96-fb52-43eb-a9c2-d4b03d11890d"
        response = self.client.post(
            url_for("comment.create"),
            data=payload,
            follow_redirects=True,
        )
        self.assert404(response)

        # comment with correct review_id
        payload["review_id"] = self.review["id"]

        # blocked user should not be allowed to comment
        db_users.block(self.commenter.id)
        response = self.client.post(
            url_for("comment.create"),
            data=payload,
            follow_redirects=True,
        )
        self.assertIn("You are not allowed to write new comments", str(response.data))
        db_users.unblock(self.commenter.id)

        # comment with some text and a valid review_id must be saved
        response = self.client.post(
            url_for("comment.create"),
            data=payload,
        )
        self.assertRedirects(response, url_for("review.entity", id=self.review["id"]))
        self.assertEqual(comment_count+1, db_comment.count_comments(review_id=self.review["id"]))

        response = self.client.get(url_for("review.entity", id=self.review["id"]))
        self.assert200(response)
        # Test that the rendered html should contain success message
        self.assertIn("Comment has been saved!", str(response.data))

    def test_delete(self):
        # create a temporary comment by commenter
        comment = self.create_dummy_comment()
        comment_count = db_comment.count_comments(review_id=self.review["id"])

        self.temporary_login(self.reviewer)

        # Other users should not be able to delete the comment by commenter
        response = self.client.post(
            url_for("comment.delete", id=comment["id"]),
            follow_redirects=True,
        )
        self.assert401(response, "Only the author can delete this comment.")

        self.temporary_login(self.commenter)

        # should return 404 on trying to delete non-existent comment
        response = self.client.post(
            url_for("comment.delete", id="false-comment"),
            follow_redirects=True
        )
        self.assert404(response)

        # GET request to by commenter to comment.delete should redirect to delete_comment template
        response = self.client.get(
            url_for("comment.delete", id=comment["id"]),
            follow_redirects=True,
        )
        self.assert200(response)
        self.assertIn("Are you sure you want to delete your comment on", str(response.data))

        # POST request by commenter to comment.delete should delete the comment
        response = self.client.post(
            url_for("comment.delete", id=comment["id"]),
            follow_redirects=True,
        )
        self.assert200(response)
        self.assertEqual(comment_count-1, db_comment.count_comments(review_id=self.review["id"]))
        self.assertIn("Comment has been deleted.", str(response.data))

    def test_edit(self):
        # create a temporary comment by commenter
        comment = self.create_dummy_comment()
        comment_count = db_comment.count_comments(review_id=self.review["id"])

        self.temporary_login(self.reviewer)

        # Other users should not be able to edit the comment by commenter
        response = self.client.post(
            url_for("comment.edit", id=comment["id"]),
            follow_redirects=True,
        )
        self.assert401(response, "Only the author can edit this comment.")

        self.temporary_login(self.commenter)

        # should return 404 on trying to edit non-existent comment
        response = self.client.post(
            url_for("comment.edit", id="false-comment"),
            follow_redirects=True
        )
        self.assert404(response)

        payload = {
            "review_id": self.review["id"],
            "text": "",
            "state": "publish",
        }

        # should be unable to add an empty comment
        response = self.client.post(
            url_for("comment.edit", id=comment["id"]),
            data=payload,
            follow_redirects=True,
        )
        self.assert200(response)
        self.assertEqual(comment_count, db_comment.count_comments(review_id=self.review["id"]))
        self.assertIn("Comment must not be empty!", str(response.data))

        # should be unable to update comment without changing comment text
        payload["text"] = "Dummy Comment"

        response = self.client.post(
            url_for("comment.edit", id=comment["id"]),
            data=payload,
            follow_redirects=True,
        )
        self.assert200(response)
        self.assertEqual(comment_count, db_comment.count_comments(review_id=self.review["id"]))
        self.assertIn("You must change some content of the comment to update it!", str(response.data))

        # should be able to update comment by changing text
        payload["text"] = "Updated comment text"

        response = self.client.post(
            url_for("comment.edit", id=comment["id"]),
            data=payload,
            follow_redirects=True,
        )
        self.assert200(response)
        self.assertEqual(comment_count, db_comment.count_comments(review_id=self.review["id"]))
        self.assertIn("Comment has been updated.", str(response.data))
