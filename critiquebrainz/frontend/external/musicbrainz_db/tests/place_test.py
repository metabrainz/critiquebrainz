from unittest import TestCase
from unittest.mock import MagicMock
from critiquebrainz.frontend.external.musicbrainz_db import place as mb_place
from critiquebrainz.frontend.external.musicbrainz_db.test_data import place_suisto, place_verkatehdas
from critiquebrainz.frontend.external.musicbrainz_db.tests import setup_cache


class PlaceTestCase(TestCase):

    def setUp(self):
        setup_cache()
        mb_place.mb_session = MagicMock()
        self.mock_db = mb_place.mb_session.return_value.__enter__.return_value
        self.place_query = self.mock_db.query.return_value.options.return_value.options.return_value.filter.return_value.all

    def test_get_by_id(self):
        self.place_query.return_value = [place_suisto]
        place = mb_place.get_place_by_id('d71ffe38-5eaf-426b-9a2e-e1f21bc84609')
        self.assertEqual(place['name'], 'Suisto')
        self.assertEqual(place['type'], 'Venue')
        self.assertDictEqual(place['coordinates'], {
            'latitude': 60.997758,
            'longitude': 24.477142
        })
        self.assertDictEqual(place['area'], {
            'id': '4479c385-74d8-4a2b-bdab-f48d1e6969ba',
            'name': 'Hämeenlinna',
        })

    def test_fetch_multiple_places(self):
        self.place_query.return_value = [place_suisto, place_verkatehdas]
        places = mb_place.fetch_multiple_places(['f9587914-8505-4bd1-833b-16a3100a4948', 'd71ffe38-5eaf-426b-9a2e-e1f21bc84609'])
        self.assertEqual(places['d71ffe38-5eaf-426b-9a2e-e1f21bc84609']['name'], 'Suisto')
        self.assertEqual(places['f9587914-8505-4bd1-833b-16a3100a4948']['name'], 'Verkatehdas')
