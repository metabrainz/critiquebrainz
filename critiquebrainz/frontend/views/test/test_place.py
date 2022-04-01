from critiquebrainz.frontend.testing import FrontendTestCase

class PlaceViewsTestCase(FrontendTestCase):

    def test_place_page(self):
        response = self.client.get('/place/bea135c0-a32e-49be-85fd-9234c73fa0a8')
        self.assert200(response)
        self.assertIn('Berliner Philharmonie', str(response.data))

        response = self.client.get('/place/bea135c0-a32e-49be-85fd-9234c73fdddd')
        self.assert404(response)
