from flask import current_app
from critiquebrainz.frontend.testing import FrontendTestCase


class AdministratorsTestCase(FrontendTestCase):

    def test_administrators(self):
        response = self.client.get('/administrators/')
        self.assert200(response)
        for admin in current_app.config['ADMINS']:
            self.assertIn(admin, response.data.decode())
