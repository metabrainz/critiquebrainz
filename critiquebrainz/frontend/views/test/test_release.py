from unittest import mock
from critiquebrainz.frontend.testing import FrontendTestCase


class ReleaseViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ReleaseViewsTestCase, self).setUp()

    @mock.patch('critiquebrainz.frontend.external.musicbrainz_db.release.get_release_by_id')
    def test_release_page(self, get_release_by_id):
        get_release_by_id.return_value = {
            'id': '57ebb904-03de-47cd-89d6-ae444a31fc88',
            'name': 'The 20/20 Experience',
            'release-group': {
                'id': 'deae6fc2-a675-4f35-9565-d2aaea4872c7',
                'name': 'The 20/20 Experience',
            }
        }

        response = self.client.get("/release/57ebb904-03de-47cd-89d6-ae444a31fc88")
        self.assertRedirects(response, "/release-group/deae6fc2-a675-4f35-9565-d2aaea4872c7")
