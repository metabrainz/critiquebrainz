from critiquebrainz.test_case import ClientTestCase


class ReleaseGroupViewsTestCase(ClientTestCase):

    def test_artist_entity_handler(self):
        response = self.client.get("/release-group/9162580e-5df4-32de-80cc-f45a8d8a9b1d")
        self.assert200(response)
