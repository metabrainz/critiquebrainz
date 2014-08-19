from critiquebrainz.frontend.testing import FrontendTestCase


class ViewsTestCase(FrontendTestCase):

    def test_release_group_page(self):
        # Basic release group page should be available.
        response = self.client.get("/release-group/c2e0ff67-fb31-4443-ae0e-22ecf010463b")
        assert response.status_code == 200
        assert "Days Are Gone" in response.data and "No reviews found" in response.data

        # TODO: Try to add review and check it's displayed there!
