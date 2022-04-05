from unittest import mock
from critiquebrainz.frontend.testing import FrontendTestCase


class ReleaseViewsTestCase(FrontendTestCase):

    def test_release_page(self):
        response = self.client.get("/release/3b5e9a42-7e0f-4a3a-935e-6231f9292126")
        self.assertRedirects(response, "/release-group/17fbcc66-f03b-4b24-9e77-0368d385e274")
