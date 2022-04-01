from critiquebrainz.frontend.testing import FrontendTestCase

class EventViewsTestCase(FrontendTestCase):

    def test_event_page(self):
        response = self.client.get('/event/fe39727a-3d21-4066-9345-3970cbd6cca4')
        self.assert200(response)
        self.assertIn('Nine Inch Nails at Arena Riga', str(response.data))

        response = self.client.get('/event/fe39727a-3d21-4066-9345-3970cbd66666')
        self.assert404(response)
