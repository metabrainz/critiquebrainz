from unittest import TestCase
from unittest.mock import MagicMock
from critiquebrainz.frontend.external.musicbrainz_db.tests import setup_cache
from critiquebrainz.frontend.external.musicbrainz_db.test_data import (
    release_numb_encore,
    release_collision_course,
    release_numb_encore_1,
)
from critiquebrainz.frontend.external.musicbrainz_db import release as mb_release


class ReleaseTestCase(TestCase):

    def setUp(self):
        setup_cache()
        mb_release.mb_session = MagicMock()
        self.mock_db = mb_release.mb_session.return_value.__enter__.return_value
        self.release_query = self.mock_db.query.return_value.options.return_value.options.return_value.\
            options.return_value.options.return_value.options.return_value.filter.return_value.all

    def test_get_by_id(self):
        self.release_query.return_value = [release_numb_encore]
        release = mb_release.get_release_by_id('16bee711-d7ce-48b0-adf4-51f124bcc0df')
        self.assertEqual(release["name"], "Numb/Encore")
        self.assertEqual(len(release["medium-list"][0]["track-list"]), 2)
        self.assertDictEqual(release["medium-list"][0]["track-list"][0], {
            "id": "dfe024b2-95b2-453f-b03e-3b9fa06f44e6",
            "name": "Numb/Encore (explicit)",
            "number": "1",
            "position": 1,
            "length": 207000,
            "recording_id": "daccb724-8023-432a-854c-e0accb6c8678",
            "recording_title": "Numb/Encore (explicit)"
        })

    def test_fetch_multiple_releases(self):
        self.mock_db.query.return_value.filter.return_value.all.return_value = [release_numb_encore_1, release_collision_course]
        releases = mb_release.fetch_multiple_releases(
            mbids=['f51598f5-4ef9-4b8a-865d-06a077bf78cf', 'a64a0467-9d7a-4ffa-90b8-d87d9b41e311'],
        )
        self.assertEqual(len(releases), 2)
        self.assertEqual(releases['a64a0467-9d7a-4ffa-90b8-d87d9b41e311']['name'], 'Numb/Encore')
        self.assertEqual(releases['f51598f5-4ef9-4b8a-865d-06a077bf78cf']['name'], 'Collision Course')
