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
        current_app.jinja_env.filters['entity_details'] = mock_get_entity_by_id

    def test_create(self):
        self.temporary_login(self.commenter)

        # empty comment should be rejected
        payload = {
            'review_id': self.review['id'],
            'text': '',
            'state': 'publish',
        }
        response = self.client.post(
            url_for('comment.create'),
            data=payload,
        )

        self.assertRedirects(response, '/review/%s' % self.review['id'])
        count = db_comment.count_comments(review_id=self.review['id'])
        self.assertEqual(count, 0)

        response = self.client.get('/review/%s' % self.review['id'])
        self.assert200(response)
        # Test that the rendered html should contain error message
        self.assertIn('Comment must not be empty!', str(response.data))
        # Test that the rendered html should contain commenter's display name only once (just above comment form)
        self.assertEqual(str(response.data).count(self.commenter.display_name), 1)

        # comment with some text should be accepted
        payload = {
            'review_id': self.review['id'],
            'text': 'Test Comment.',
            'state': 'publish',
        }
        response = self.client.post(
            url_for('comment.create'),
            data=payload,
        )

        self.assertRedirects(response, '/review/%s' % self.review['id'])
        count = db_comment.count_comments(review_id=self.review['id'])
        self.assertEqual(count, 1)

        response = self.client.get('/review/%s' % self.review['id'])
        self.assert200(response)
        # Test that the rendered html should contain success message
        self.assertIn('Comment has been saved!', str(response.data))
        # Test that the rendered html should contain commenter's display name twice (above posted comment and comment form)
        self.assertEqual(str(response.data).count(self.commenter.display_name), 2)
