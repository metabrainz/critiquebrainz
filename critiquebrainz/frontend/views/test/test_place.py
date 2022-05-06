from critiquebrainz.frontend.testing import FrontendTestCase

class PlaceViewsTestCase(FrontendTestCase):

    def test_place_page(self):
        response = self.client.get('/place/853b36f9-8806-459c-9480-0766b8f9354b')
        self.assert200(response)
        self.assertIn('Xfinity Center', str(response.data))

        response = self.client.get('/place/61648164-abca-4679-9ccb-1cf350efb349')
        self.assert404(response)

        # Concerts tab
        response = self.client.get('/place/853b36f9-8806-459c-9480-0766b8f9354b?event_type=concert')
        self.assert200(response)
        self.assertIn('Chicago at Xfinity Center', str(response.data))

        # Festivals tab
        response = self.client.get('/place/853b36f9-8806-459c-9480-0766b8f9354b?event_type=festival')
        self.assert200(response)
        self.assertIn('Ozzfest 1997 in Mansfield', str(response.data))

        # Other events tab
        response = self.client.get('/place/853b36f9-8806-459c-9480-0766b8f9354b?event_type=other')
        self.assert200(response)
