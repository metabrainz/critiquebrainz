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

import critiquebrainz.db.license as db_license
import critiquebrainz.db.review as db_review
import critiquebrainz.db.users as db_users
from critiquebrainz.db.user import User
from critiquebrainz.frontend.testing import FrontendTestCase


class StatisticsViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(StatisticsViewsTestCase, self).setUp()
        self.user = User(db_users.get_or_create(1, "aef06569-098f-4218-a577-b413944d9493", new_user_data={
            "display_name": u"Tester",
        }))
        self.license = db_license.create(
            id="CC BY-SA 3.0",
            full_name="Test License.",
        )

        # totally disable cache get or set
        cache.gen_key = MagicMock(return_value=None)
        cache.get = MagicMock(return_value=None)
        cache.set = MagicMock(return_value=None)

    def test_statistics(self):
        # test when there is no user
        response = self.client.get("statistics/")
        self.assert200(response)
        self.assertIn("Could not fetch results! Please try again.", str(response.data))

        # creating a review
        db_review.create(
            entity_id="e7aad618-fa86-3983-9e77-405e21796eca",
            entity_type="release_group",
            text="Test review",
            user_id=self.user.id,
            is_draft=False,
            license_id=self.license["id"],
        )

        # test user's name in statistics page after user added review
        response = self.client.get("statistics/")
        self.assert200(response)
        self.assertIn(self.user.display_name, str(response.data))
