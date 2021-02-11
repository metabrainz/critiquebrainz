from unittest import mock

from critiquebrainz.frontend.testing import FrontendTestCase


def return_release_groups(*, artist_id, release_types=None, limit=None, offset=None):
    # pylint: disable=unused-argument
    if release_types == ['ep']:
        return [{
            'id': '8ef859e3-feb2-4dd1-93da-22b91280d768',
            'title': 'Collision Course',
            'first-release-year': 2004,
        }], 1
    if release_types == ['single']:
        return [{
            'id': '7c1014eb-454c-3867-8854-3c95d265f8de',
            'title': 'Numb/Encore',
            'first-release-year': 2004,
        }], 1
    if release_types == ['album']:
        return [{
            'id': '65404106-2976-4f98-a0e2-4e76923ea06d',
            'title': 'A Thousand Suns',
            'first-release-year': 2010,
        }], 1
    return [], 0


class ArtistViewsTestCase(FrontendTestCase):

    @mock.patch('critiquebrainz.frontend.external.musicbrainz_db.release_group.browse_release_groups')
    @mock.patch('critiquebrainz.frontend.external.musicbrainz_db.artist.get_artist_by_id')
    def test_artist_page(self, get_artist_by_id, browse_release_groups):
        get_artist_by_id.return_value = {
            'id': 'f59c5520-5f46-4d2c-b2c4-822eabf53419',
            'name': 'Linkin Park',
            'sort-name': 'Linkin Park',
        }
        browse_release_groups.side_effect = return_release_groups
        # Basic artist page should be available.
        response = self.client.get('/artist/f59c5520-5f46-4d2c-b2c4-822eabf53419')
        self.assert200(response)
        self.assertIn('Linkin Park', str(response.data))

        # Album tab
        response = self.client.get('/artist/f59c5520-5f46-4d2c-b2c4-822eabf53419?release_type=album')
        self.assert200(response)
        self.assertIn('A Thousand Suns', str(response.data))

        # Singles tab
        response = self.client.get('/artist/f59c5520-5f46-4d2c-b2c4-822eabf53419?release_type=single')
        self.assert200(response)
        self.assertIn('Numb/Encore', str(response.data))

        # EPs tab
        response = self.client.get('/artist/f59c5520-5f46-4d2c-b2c4-822eabf53419?release_type=ep')
        self.assert200(response)
        self.assertIn('Collision Course', str(response.data))

        # Broadcasts tab
        response = self.client.get('/artist/f59c5520-5f46-4d2c-b2c4-822eabf53419?release_type=broadcast')
        self.assert200(response)

        # Other releases tab
        response = self.client.get('/artist/f59c5520-5f46-4d2c-b2c4-822eabf53419?release_type=other')
        self.assert200(response)
