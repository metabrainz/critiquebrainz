from unittest import mock
from critiquebrainz.frontend.testing import FrontendTestCase

def return_release_groups(*, label_id, release_types=None, limit=None, offset=None):
    # pylint: disable=unused-argument
    if release_types == ['ep']:
        return [{
            'mbid': '7c2af926-8389-44fd-8a9f-4bb2d365c274',
            'title': 'Music for Mandolin and Fortepiano',
            'first-release-year': 2020,
        }], 1
    if release_types == ['single']:
        return [{
            'mbid': 'd6b50fd0-7e03-408f-89a9-6b426a66fbdb',
            'title': 'I Have Dreamed',
            'first-release-year': 2020,
        }], 1
    if release_types == ['album']:
        return [{
            'mbid': '2d9791bb-b5db-402c-8a3c-a5160a87dee3',
            'title': 'Piano Jewels',
            'first-release-year': 2022,
        }], 1
    if release_types == ['other']:
        return [{
            'mbid': '85bc17b0-5c57-4611-ad2f-ab05fc2687c0',
            'title': 'The Choral Collection',
            'first-release-year': 2019,
        }], 1
    return [], 0

class LabelViewsTestCase(FrontendTestCase):

    @mock.patch('critiquebrainz.frontend.external.musicbrainz_db.release_group.get_release_groups_for_label')
    def test_label_page(self, get_release_groups_for_label):
        # Release groups in the sample database don't have all possible rg types, so mock it
        get_release_groups_for_label.side_effect = return_release_groups

        # Basic label page should be available.
        response = self.client.get('/label/615fa478-3901-42b8-80bc-bf58b1ff0e03')
        self.assert200(response)
        self.assertIn('Naxos', str(response.data))

        # Album tab
        response = self.client.get('/label/615fa478-3901-42b8-80bc-bf58b1ff0e03?release_type=album')
        self.assert200(response)
        self.assertIn('Piano Jewels', str(response.data))

        # Singles tab
        response = self.client.get('/label/615fa478-3901-42b8-80bc-bf58b1ff0e03?release_type=single')
        self.assert200(response)
        self.assertIn('I Have Dreamed', str(response.data))

        # EPs tab
        response = self.client.get('/label/615fa478-3901-42b8-80bc-bf58b1ff0e03?release_type=ep')
        self.assert200(response)
        self.assertIn('Music for Mandolin and Fortepiano', str(response.data))

        # Broadcasts tab
        response = self.client.get('/label/615fa478-3901-42b8-80bc-bf58b1ff0e03?release_type=broadcast')
        self.assert200(response)
        
        # Other releases tab
        response = self.client.get('/label/615fa478-3901-42b8-80bc-bf58b1ff0e03?release_type=other')
        self.assert200(response)
        self.assertIn('The Choral Collection', str(response.data))

        # No such mbid returns an error
        response = self.client.get('/label/615fa478-3901-42b8-80bc-bf58b1ff0000')
        self.assert404(response)
