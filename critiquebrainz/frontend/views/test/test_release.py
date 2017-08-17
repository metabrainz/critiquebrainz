from unittest.mock import MagicMock
from critiquebrainz.frontend.testing import FrontendTestCase
import critiquebrainz.frontend.external.musicbrainz_db.release as mb_release


class ReleaseViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ReleaseViewsTestCase, self).setUp()
        mb_release.get_release_by_id = MagicMock()
        mb_release.get_release_by_id.return_value = {
            'id': '57ebb904-03de-47cd-89d6-ae444a31fc88',
            'name': 'The 20/20 Experience',
            'release-group': {
                'id': 'deae6fc2-a675-4f35-9565-d2aaea4872c7',
                'name': 'The 20/20 Experience',
            }
        }

    def test_release_page(self):
        response = self.client.get("/release/57ebb904-03de-47cd-89d6-ae444a31fc88")
        self.assertRedirects(response, "/release-group/deae6fc2-a675-4f35-9565-d2aaea4872c7")
