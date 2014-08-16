from critiquebrainz.frontend.testing import FrontendTestCase


class ViewsTestCase(FrontendTestCase):

    def test_artist_page(self):
        # Basic artist page should be available.
        response = self.client.get("/artist/aef06569-098f-4218-a577-b413944d9493")
        assert response.status_code == 200
        assert "HAIM" in response.data

        # Album tab
        response = self.client.get("/artist/aef06569-098f-4218-a577-b413944d9493?release_type=album")
        assert response.status_code == 200
        assert "Days Are Gone" in response.data

        # Singles tab
        response = self.client.get("/artist/aef06569-098f-4218-a577-b413944d9493?release_type=single")
        assert response.status_code == 200
        assert "The Wire" in response.data

        # EPs tab
        response = self.client.get("/artist/aef06569-098f-4218-a577-b413944d9493?release_type=ep")
        assert response.status_code == 200
        assert "Forever" in response.data

        # Broadcasts tab
        response = self.client.get("/artist/aef06569-098f-4218-a577-b413944d9493?release_type=broadcast")
        assert response.status_code == 200

        # Other releases tab
        response = self.client.get("/artist/aef06569-098f-4218-a577-b413944d9493?release_type=other")
        assert response.status_code == 200
