from unittest import mock

from critiquebrainz.frontend.testing import FrontendTestCase

def return_events(*, place_id, event_types=None, limit=None, offset=None):
    # pylint: disable=unused-argument
    if event_types == ['concert']:
        return [{
            'mbid': 'd6dbb3d3-de2d-4052-aeac-6ae94f291d37',
            'name': 'Organ Recital',
            'life-span': {
                'begin': '2021-09-04',
                'end': '2021-09-04',
            },
        }], 1
    if event_types == ['festival']:
        return [{
            'mbid': '0415b420-f1ee-4b4b-b149-70095f8d568a',
            'name': 'The Proms 2021',
            'life-span': {
                'begin': '2021-07-30',
                'end': '2021-09-11',
            },
        }], 1
    return [], 0


class PlaceViewsTestCase(FrontendTestCase):

    @mock.patch('critiquebrainz.frontend.external.musicbrainz_db.event.get_event_for_place')
    def test_place_page(self, get_event_for_place):
        # Events in the sample database don't have all possible event types, so mock it
        get_event_for_place.side_effect = return_events

        response = self.client.get('/place/bea135c0-a32e-49be-85fd-9234c73fa0a8')
        self.assert200(response)
        self.assertIn('Berliner Philharmonie', str(response.data))

        response = self.client.get('/place/bea135c0-a32e-49be-85fd-9234c73fdddd')
        self.assert404(response)

        # Concerts tab
        response = self.client.get('/place/4352063b-a833-421b-a420-e7fb295dece0?event_type=concert')
        self.assert200(response)
        self.assertIn('Organ Recital', str(response.data))

        # Festivals tab
        response = self.client.get('/place/4352063b-a833-421b-a420-e7fb295dece0?event_type=festival')
        self.assert200(response)
        self.assertIn('The Proms 2021', str(response.data))

        # Other events tab
        response = self.client.get('/place/4352063b-a833-421b-a420-e7fb295dece0?event_type=other')
        self.assert200(response)
