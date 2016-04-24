from critiquebrainz.frontend.testing import FrontendTestCase


class ReleaseGroupViewsTestCase(FrontendTestCase):

    def test_release_group_page(self):
        # Basic release group page should be available.
        response = self.client.get("/release-group/c2e0ff67-fb31-4443-ae0e-22ecf010463b")
        self.assert200(response)
        self.assertIn("Days Are Gone", str(response.data))
        self.assertIn("No reviews found", str(response.data))
        # TODO(roman): Try to add review and check it's displayed there!
