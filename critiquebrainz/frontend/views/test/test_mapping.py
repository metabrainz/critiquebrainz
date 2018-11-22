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

from unittest.mock import MagicMock
from critiquebrainz.frontend.testing import FrontendTestCase
from critiquebrainz.db.user import User
import critiquebrainz.db.users as db_users
from critiquebrainz.frontend.external import mbspotify
import critiquebrainz.frontend.external.spotify as spotify_api
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
import critiquebrainz.frontend.external.musicbrainz_db.release_group as mb_release_group

class SpotifyMappingViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(SpotifyMappingViewsTestCase, self).setUp()
        self.user = User(db_users.get_or_create(1, "aef06569-098f-4218-a577-b413944d9493", new_user_data={
            "display_name": u"Tester",
        }))

        self.test_spotify_id = "6IH6co1QUS7uXoyPDv0rIr"
        self.test_release_groups = {
            'id': '6b3cd75d-7453-39f3-86c4-1441f360e121',
            'title': 'Test Release Group',
            'first-release-year': 1970,
            'artist-credit': [{
                'name': 'Test Artist'
            }]
        }
        self.test_spotify_response = {
            '6IH6co1QUS7uXoyPDv0rIr': {
                'type': 'album',
                'id': '6IH6co1QUS7uXoyPDv0rIr',
                'name': 'Test Album',
                'release_date': '1970-01-01',
                'external_urls': {
                    'spotify': 'https://open.spotify.com/album/6IH6co1QUS7uXoyPDv0rIr'
                },
                'artists': [{'name': 'Test Artist', }]
            }
        }

    def test_false_release_group_mapping_list(self):
        # test mapping for non-existent release group, should return 404
        mbspotify.mappings = MagicMock(return_value=[])
        mb_release_group.get_release_group_by_id = MagicMock(side_effect=mb_exceptions.NoDataFoundException)
        response = self.client.get("/mapping/6b3cd75d-7453-39f3-86c4-1441f360e121")
        self.assert404(response, "Can't find release group with a specified ID.")

    def test_release_group_mapping_list(self):
        # test release group with mappings
        mbspotify.mappings = MagicMock(return_value=['spotify:album:6IH6co1QUS7uXoyPDv0rIr'])
        spotify_api.get_multiple_albums = MagicMock(return_value=self.test_spotify_response)
        mb_release_group.get_release_group_by_id = MagicMock(return_value=self.test_release_group)
        response = self.client.get("/mapping/6b3cd75d-7453-39f3-86c4-1441f360e121")
        self.assert200(response)
        self.assertIn(self.test_spotify_id, str(response.data))
        self.assertIn("Test Album", str(response.data))
        self.assertIn("1970-01-01", str(response.data))

    def test_release_group_no_mappings(self):
        # testing for release group with no mappings
        mbspotify.mappings = MagicMock(return_value=[])
        mb_release_group.get_release_group_by_id = MagicMock(return_value=self.test_release_groups)
        response = self.client.get("/mapping/6b3cd75d-7453-39f3-86c4-1441f360e121")
        self.assert200(response)
        self.assertIn("No mappings", str(response.data))
