from unittest import TestCase
from unittest.mock import MagicMock
from critiquebrainz.frontend.external.musicbrainz_db import release_group as mb_release_group
from critiquebrainz.frontend.external.musicbrainz_db.test_data import releasegroup_numb_encore, releasegroup_collision_course
from critiquebrainz.frontend.external.musicbrainz_db.tests import setup_cache


class ReleaseGroupTestCase(TestCase):

    def setUp(self):
        setup_cache()
        mb_release_group.mb_session = MagicMock()
        self.mock_db = mb_release_group.mb_session.return_value.__enter__.return_value
        # Mock sql query for fetching release groups and alter the return value to return SQLAlchemy objects.
        self._release_group_query = self.mock_db.query.return_value.options.return_value.options.return_value
        self._release_group_query_with_artists = self._release_group_query.options.return_value.options.return_value.\
            options.return_value
        self.release_group_query = self._release_group_query.filter.return_value.all
        self.release_group_query_with_artists = self._release_group_query_with_artists.filter.return_value.all

    def test_get_by_id(self):
        self.release_group_query_with_artists.return_value = [releasegroup_numb_encore]
        release_group = mb_release_group.get_release_group_by_id(
            '7c1014eb-454c-3867-8854-3c95d265f8de',
        )

        self.assertEqual(release_group['id'], '7c1014eb-454c-3867-8854-3c95d265f8de')
        self.assertEqual(release_group['title'], 'Numb/Encore')
        # Check if multiple artists are properly fetched
        self.assertEqual(release_group['artist-credit-phrase'], 'Jay-Z/Linkin Park')
        self.assertDictEqual(release_group['artist-credit'][0], {
            'name': 'Jay-Z',
            'artist': {
                'id': 'f82bcf78-5b69-4622-a5ef-73800768d9ac',
                'name': 'JAY Z',
                'sort_name': 'JAY Z'
            },
            'join_phrase': '/',
        })
        self.assertDictEqual(release_group['artist-credit'][1], {
            'name': 'Linkin Park',
            'artist': {
                'id': 'f59c5520-5f46-4d2c-b2c4-822eabf53419',
                'name': 'Linkin Park',
                'sort_name': 'Linkin Park',
            },
        })

    def test_fetch_release_groups(self):
        self.release_group_query.return_value = [releasegroup_numb_encore, releasegroup_collision_course]
        release_groups = mb_release_group.fetch_multiple_release_groups(
            mbids=['8ef859e3-feb2-4dd1-93da-22b91280d768', '7c1014eb-454c-3867-8854-3c95d265f8de'],
        )
        self.assertEqual(len(release_groups), 2)
        self.assertEqual(release_groups['7c1014eb-454c-3867-8854-3c95d265f8de']['title'], 'Numb/Encore')
        self.assertEqual(release_groups['8ef859e3-feb2-4dd1-93da-22b91280d768']['title'], 'Collision Course')

    def test_fetch_browse_release_groups(self):
        mb_release_group._browse_release_groups_query = MagicMock()
        mock_query = mb_release_group._browse_release_groups_query.return_value
        mock_query.count.return_value = 2
        mock_query.order_by.return_value.limit.return_value.offset.\
            return_value.all.return_value = [releasegroup_collision_course, releasegroup_numb_encore]
        release_groups = mb_release_group.browse_release_groups(
            artist_id='f59c5520-5f46-4d2c-b2c4-822eabf53419',
            release_types=['Single', 'EP'],
        )
        self.assertListEqual(release_groups[0], [
            {
                'id': '8ef859e3-feb2-4dd1-93da-22b91280d768',
                'title': 'Collision Course',
                'first-release-year': 2004,
            },
            {
                'id': '7c1014eb-454c-3867-8854-3c95d265f8de',
                'title': 'Numb/Encore',
                'first-release-year': 2004,
            }
        ])
        self.assertEqual(release_groups[1], 2)
