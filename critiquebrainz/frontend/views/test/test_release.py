from critiquebrainz.frontend.testing import FrontendTestCase


class ReleaseViewsTestCase(FrontendTestCase):

    def test_release_page(self):
        response = self.client.get("/release/4a3541a7-db1d-4da2-a36b-172c5f8b2cc4")
        self.assertRedirects(response, "/release-group/4d1e6020-324d-4e8c-af1d-c7a2525a15ee")
