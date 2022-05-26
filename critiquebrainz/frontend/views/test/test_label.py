from critiquebrainz.frontend.testing import FrontendTestCase

class LabelViewsTestCase(FrontendTestCase):

    def test_label_page(self):

        # Basic label page should be available.
        response = self.client.get('/label/c029628b-6633-439e-bcee-ed02e8a338f7')
        self.assert200(response)
        self.assertIn('EMI', str(response.data))

        # Album tab
        response = self.client.get('/label/c029628b-6633-439e-bcee-ed02e8a338f7?release_type=album')
        self.assert200(response)
        self.assertIn('Discovery', str(response.data))

        # Singles tab
        response = self.client.get('/label/c029628b-6633-439e-bcee-ed02e8a338f7?release_type=single')
        self.assert200(response)
        self.assertIn('Besser gehts nicht', str(response.data))

        # EPs tab
        response = self.client.get('/label/c029628b-6633-439e-bcee-ed02e8a338f7?release_type=ep')
        self.assert200(response)
        self.assertIn('Potpourri', str(response.data))

        # Broadcasts tab
        response = self.client.get('/label/c029628b-6633-439e-bcee-ed02e8a338f7?release_type=broadcast')
        self.assert200(response)
        self.assertIn('No releases found', str(response.data))
        
        # Other releases tab
        response = self.client.get('/label/c029628b-6633-439e-bcee-ed02e8a338f7?release_type=other')
        self.assert200(response)
        self.assertIn('Lollipops', str(response.data))

        # No such mbid returns an error
        response = self.client.get('/label/c029628b-6633-439e-bcee-ed02e8a338f3')
        self.assert404(response)
