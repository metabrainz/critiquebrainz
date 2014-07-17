from critiquebrainz.test_case import ClientTestCase


class ArtistViewsTestCase(ClientTestCase):

    def test_artist_entity_handler(self):
        response = self.client.get("/artist/b10bbbfc-cf9e-42e0-be17-e2c3e1d2600d")
        self.assert200(response)
