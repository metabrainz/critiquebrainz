from critiquebrainz.frontend.testing import FrontendTestCase

class LabelViewsTestCase(FrontendTestCase):

    def test_label_page(self):
        response = self.client.get('/label/615fa478-3901-42b8-80bc-bf58b1ff0e03')
        self.assert200(response)
        self.assertIn('Naxos', str(response.data))

        response = self.client.get('/label/615fa478-3901-42b8-80bc-bf58b1ff0000')
        self.assert404(response)
