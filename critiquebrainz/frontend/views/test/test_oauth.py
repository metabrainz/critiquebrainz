from flask import url_for
import critiquebrainz.db.oauth_client as db_oauth_client
import critiquebrainz.db.oauth_grant as db_oauth_grant
import critiquebrainz.db.users as db_users
from critiquebrainz.frontend.testing import FrontendTestCase

from urllib.parse import urlparse, parse_qs


class OauthTestCase(FrontendTestCase):
    def setUp(self):
        from critiquebrainz.db.user import User
        self.user = User(db_users.get_or_create(2, "9371e5c7-5995-4471-a5a9-33481f897f9c", new_user_data={
            "display_name": u"User",
        }))
        self.oauthclient = db_oauth_client.create(
            user_id=self.user.id, 
            name='An oauth app',
            desc='This is a great client', 
            website='https://example.com', 
            redirect_uri='https://example.com/redirect'
        )


    def test_invalid_clientid(self):
        self.temporary_login(self.user)
        response = self.client.get(url_for('oauth.authorize_prompt', response_type='code', client_id='not-an-id', redirect_uri='x', scope='x', state='x'))
        assert response.status_code == 400
        assert "400 Bad Request: Client authentication failed." in response.text

    def test_invalid_redirect_uri(self):
        self.temporary_login(self.user)
        client_id = self.oauthclient["client_id"]
        response = self.client.get(url_for('oauth.authorize_prompt', response_type='code', client_id=client_id, redirect_uri='x', scope='x', state='x'))
        assert response.status_code == 400
        assert "400 Bad Request: Invalid redirect uri." in response.text

    def test_invalid_scope(self):
        self.temporary_login(self.user)
        client_id = self.oauthclient["client_id"]
        redirect_uri = self.oauthclient["redirect_uri"]
        response = self.client.get(url_for('oauth.authorize_prompt', response_type='code', client_id=client_id, redirect_uri=redirect_uri, scope='x', state='x'))
        assert response.status_code == 400
        assert "400 Bad Request: The requested scope is invalid, unknown, or malformed." in response.text

    def test_valid_oauth_request(self):
        self.temporary_login(self.user)
        client_id = self.oauthclient["client_id"]
        redirect_uri = self.oauthclient["redirect_uri"]
        response = self.client.get(url_for('oauth.authorize_prompt', response_type='code', client_id=client_id, redirect_uri=redirect_uri, scope='review', state='x'))
        assert response.status_code == 200
        assert "Do you want to give access to your account to An oauth app?" in response.text
        
    def test_approve_invalid_parameter(self):
        """Same endpoint, but a POST with an invalid client id"""
        self.temporary_login(self.user)
        response = self.client.post(url_for('oauth.authorize_prompt', response_type='code', client_id='x', redirect_uri='y', scope='review', state='x'))
        assert response.status_code == 400
        assert "400 Bad Request: Client authentication failed." in response.text

    def test_approve_application(self):
        """A POST to approve an oauth authorization"""
        self.temporary_login(self.user)
        client_id = self.oauthclient["client_id"]
        redirect_uri = self.oauthclient["redirect_uri"]
        response = self.client.post(url_for('oauth.authorize_prompt', response_type='code', client_id=client_id, redirect_uri=redirect_uri, scope='review', state='x'))
        assert response.status_code == 302
        # This is the redirect URL that we set in the oauth client
        assert response.location.startswith('https://example.com/redirect?code=')

        redirect_location = urlparse(response.location)
        query = parse_qs(redirect_location.query)
        assert query['state'] == ['x']
        code = query['code'][0]

        grants = db_oauth_grant.list_grants(client_id=client_id, code=code)
        assert len(grants) == 1
