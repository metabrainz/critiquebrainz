from critiquebrainz.data.testing import DataTestCase
from critiquebrainz.data.model.oauth_client import OAuthClient
from critiquebrainz.data.model.user import User


class OAuthClientTestCase(DataTestCase):
    def setUp(self):
        super(OAuthClientTestCase, self).setUp()
        self.user = User.get_or_create(u'Author', u'189d7863-d23c-49d9-ae7e-031b41qb2805')

    def test_create(self):
        self.assertEqual(OAuthClient.query.count(), 0)

        new_client = OAuthClient.create(
            user=self.user,
            name=u'Test App',
            desc=u'Application for testing.',
            website=u'https://example.com',
            redirect_uri=u'https://example.com/oauth',
        )

        clients = OAuthClient.query.all()
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0].name, u'Test App')

        self.assertEqual(len(clients[0].client_id), 20)
        self.assertEqual(len(clients[0].client_secret), 40)

    def test_delete(self):
        oauth_client = OAuthClient.create(
            user=self.user,
            name=u'Test App',
            desc=u'Application for testing.',
            website=u'https://example.com',
            redirect_uri=u'https://example.com/oauth',
        )
        self.assertEqual(OAuthClient.query.count(), 1)

        oauth_client.delete()
        self.assertEqual(OAuthClient.query.count(), 0)

    def test_to_dict(self):
        oauth_client = OAuthClient.create(
            user=self.user,
            name=u'Test App',
            desc=u'Application for testing.',
            website=u'https://example.com',
            redirect_uri=u'https://example.com/oauth',
        )
        self.assertDictEqual(
            oauth_client.to_dict(),
            {
                'client_id': oauth_client.client_id,
                'client_secret': oauth_client.client_secret,
                'user_id': oauth_client.user_id,
                'name': oauth_client.name,
                'desc': oauth_client.desc,
                'website': oauth_client.website,
                'redirect_uri': oauth_client.redirect_uri,
            }
        )

    def test_update(self):
        oauth_client = OAuthClient.create(
            user=self.user,
            name=u'Test App',
            desc=u'Application for testing.',
            website=u'https://example.com',
            redirect_uri=u'https://example.com/oauth',
        )

        oauth_client.update(
            name=u'Updated App',
            desc=u'Completely new app for testing.',
            website=u'https://example.org',
            redirect_uri=u'https://example.org/oauth',
        )

        client = OAuthClient.query.all()[0]
        self.assertEqual(client.name, u'Updated App')
        self.assertEqual(client.desc, u'Completely new app for testing.')
        self.assertEqual(client.website, u'https://example.org')
        self.assertEqual(client.redirect_uri, u'https://example.org/oauth')
