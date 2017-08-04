from unittest.mock import MagicMock
from critiquebrainz.frontend.testing import FrontendTestCase
import critiquebrainz.frontend.external.musicbrainz_db.release_group as mb_release_group


class ReleaseGroupViewsTestCase(FrontendTestCase):

    def setUp(self):
        super(ReleaseGroupViewsTestCase, self).setUp()
        mb_release_group.get_release_group_by_id = MagicMock()
        mb_release_group.get_release_group_by_id.return_value = {
            'id': '8ef859e3-feb2-4dd1-93da-22b91280d768',
            'title': 'Collision Course',
            'first-release-year': 2004,
        }

    def test_release_group_page(self):
        response = self.client.get('/release-group/8ef859e3-feb2-4dd1-93da-22b91280d768')
        self.assert200(response)
        self.assertIn('Collision Course', str(response.data))
