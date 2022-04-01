from critiquebrainz.frontend.testing import FrontendTestCase


class WorkViewsTestCase(FrontendTestCase):

    def test_work_page(self):
        response = self.client.get('/work/239389e0-305f-34fc-9147-d5c40332d112')
        self.assert200(response)
        self.assertIn('Piano Trio in A minor', str(response.data))

        response = self.client.get('/work/239389e0-305f-34fc-9147-d5c403324444')
        self.assert404(response)
