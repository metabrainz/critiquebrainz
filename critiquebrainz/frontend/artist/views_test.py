from critiquebrainz.frontend.testing import FrontendTestCase


class ArtistViewsTestCase(FrontendTestCase):

    def test_artist_page(self):
        # Basic artist page should be available.
        response = self.client.get("/artist/aef06569-098f-4218-a577-b413944d9493")
        self.assert200(response)
        self.assertIn("HAIM", response.data)

        # Album tab
        response = self.client.get("/artist/aef06569-098f-4218-a577-b413944d9493?release_type=album")
        self.assert200(response)
        self.assertIn("Days Are Gone", response.data)

        # Singles tab
        response = self.client.get("/artist/aef06569-098f-4218-a577-b413944d9493?release_type=single")
        self.assert200(response)
        self.assertIn("The Wire", response.data)

        # EPs tab
        response = self.client.get("/artist/aef06569-098f-4218-a577-b413944d9493?release_type=ep")
        self.assert200(response)
        self.assertIn("Forever", response.data)

        # Broadcasts tab
        response = self.client.get("/artist/aef06569-098f-4218-a577-b413944d9493?release_type=broadcast")
        self.assert200(response)

        # Other releases tab
        response = self.client.get("/artist/aef06569-098f-4218-a577-b413944d9493?release_type=other")
        self.assert200(response)
