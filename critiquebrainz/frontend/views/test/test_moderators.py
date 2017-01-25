from flask import current_app
from critiquebrainz.frontend.testing import FrontendTestCase


class ModeratorsTestCase(FrontendTestCase):

    def test_moderators(self):
        response = self.client.get('/moderators/')
        self.assert200(response)
        for admin in current_app.config['ADMINS']:
            self.assertIn(admin, response.data.decode())
