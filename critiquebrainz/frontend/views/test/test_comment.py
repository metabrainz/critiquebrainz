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

from critiquebrainz.db.user import User
from critiquebrainz.frontend.testing import FrontendTestCase


class CommentViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(CommentViewsTestCase, self).setUp()
        self.user = User(db_users.get_or_create(1, "aef06569-098f-4218-a577-b413944d9493", new_user_data={
            "display_name": u"Tester",
        }))
        self.license = db_license.create(
            id="CC BY-SA 3.0",
            full_name="Created so we can fill the form correctly.",
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

    def test_create(self):
        self.temporary_login(self.user)
        payload = {
            'review_id': self.review['id'],
            'text': 'Hello, this is a comment!',
            'state': 'publish',
        }
        r = self.client.post(
            '/comments/create',
            data=payload,
        )

        self.assertRedirects(r, '/review/%s' % self.review['id'])
        count = db_comment.count_comments(review_id=self.review['id'])
        self.assertEqual(count, 1)
