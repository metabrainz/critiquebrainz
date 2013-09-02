from flask import url_for, session
from flask.ext.login import current_user
from rauth import OAuth2Service
from critiquebrainz.utils import build_url
from critiquebrainz.exceptions import APIError
import requests
import json

class CritiqueBrainzAPI(object):

    def __init__(self, base_url, client_id, **kwargs):
        self.base_url = base_url
        self.client_id = client_id
        self._service = OAuth2Service(base_url=base_url,
                                      client_id=client_id,
                                      **kwargs)

    def generate_twitter_authorization_uri(self):
        params = dict(response_type='code',
                      redirect_uri=url_for('login.post', _external=True),
                      scope='user authorization publication client',
                      client_id=self.client_id)
        return build_url(self.base_url+'login/twitter', params)

    def generate_musicbrainz_authorization_uri(self):
        params = dict(response_type='code',
                      redirect_uri=url_for('login.post', _external=True),
                      scope='user authorization publication client',
                      client_id=self.client_id)
        return build_url(self.base_url+'login/musicbrainz', params)

    def get_token_from_code(self, code):
        data = dict(grant_type='code',
                    code=code,
                    scope='user authorization publication client',
                    redirect_uri=url_for('login.post', _external=True))
        resp = self._service.get_raw_access_token(data=data).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        access_token = resp.get('access_token')
        refresh_token = resp.get('refresh_token')
        expires_in = resp.get('expires_in')
        return access_token, refresh_token, expires_in

    def get_token_from_refresh_token(self, refresh_token):
        data = dict(grant_type='refresh_token',
                    refresh_token=refresh_token,
                    scope='user authorization publication client')
        resp = self._service.get_raw_access_token(data=data).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        access_token = resp.get('access_token')
        refresh_token = resp.get('refresh_token')
        expires_in = resp.get('expires_in')
        return access_token, refresh_token, expires_in

    def get_me(self, access_token):
        session = self._service.get_session(access_token)
        resp = session.get('user/me').json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        me = resp.get('user')
        return me

    def validate_oauth_request(self, client_id, response_type, redirect_uri, scope):
        data = dict(client_id=client_id,
                    response_type=response_type,
                    redirect_uri=redirect_uri,
                    scope=scope)
        resp = requests.post(self.base_url+'oauth/validate', data=data).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        client = resp.get('client')
        return client

    def authorize(self, client_id, response_type, redirect_uri, scope, access_token):
        data = dict(client_id=client_id,
                    response_type=response_type,
                    redirect_uri=redirect_uri,
                    scope=scope)
        session = self._service.get_session(access_token)
        resp = session.post('oauth/authorize', data=data).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        code = resp.get('code')
        return code

    def get_publication(self, id):
        resp = requests.get(self.base_url+'publication/%s' % id).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        publication = resp.get('publication')
        return publication

    def get_me_publications(self, access_token, sort, limit, offset):
        params = dict(sort=sort, limit=limit, offset=offset)
        session = self._service.get_session(access_token)
        resp = session.get('user/me/publications', params=params).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        count = resp.get('count')
        publications = resp.get('publications')
        return count, publications

    def get_me_clients(self, access_token):
        session = self._service.get_session(access_token)
        resp = session.get('user/me/clients').json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        clients = resp.get('clients')
        return clients

    def get_me_tokens(self, access_token):
        session = self._service.get_session(access_token)
        resp = session.get('user/me/tokens').json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        tokens = resp.get('tokens')
        return tokens

    def get_client(self, id, access_token):
        session = self._service.get_session(access_token)
        resp = session.get('client/%s' % id).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        client = resp.get('client')
        return client

    def create_client(self, name, desc, website, redirect_uri, scopes, access_token):
        session = self._service.get_session(access_token)
        data = dict(name=name,
                    desc=desc,
                    website=website,
                    redirect_uri=redirect_uri,
                    scopes=scopes)
        headers = {'Content-type': 'application/json'}
        resp = session.post('client/', data=json.dumps(data), headers=headers).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        message = resp.get('message')
        client = resp.get('client')
        client_id = client.get('id')
        client_secret = client.get('secret')
        return message, client_id, client_secret

    def create_publication(self, release_group, text, access_token):
        session = self._service.get_session(access_token)
        data = dict(release_group=release_group,
                    text=text)
        headers = {'Content-type': 'application/json'}
        resp = session.post('publication/', data=json.dumps(data), headers=headers).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        message = resp.get('message')
        id = resp.get('id')
        return message, id

    def update_publication(self, id, access_token, **kwargs):
        session = self._service.get_session(access_token)
        data = kwargs
        headers = {'Content-type': 'application/json'}
        resp = session.post('publication/%s' % id, data=json.dumps(data), headers=headers).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def update_profile(self, access_token, **kwargs):
        session = self._service.get_session(access_token)
        data = kwargs
        headers = {'Content-type': 'application/json'}
        resp = session.post('user/me', data=json.dumps(data), headers=headers).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def update_client(self, id, access_token, **kwargs):
        session = self._service.get_session(access_token)
        data = kwargs
        headers = {'Content-type': 'application/json'}
        resp = session.post('client/%s' % id, data=json.dumps(data), headers=headers).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_publication(self, id, access_token):
        session = self._service.get_session(access_token)
        resp = session.delete('publication/%s' % id).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_profile(self, access_token):
        session = self._service.get_session(access_token)
        resp = session.delete('user/me').json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_client(self, id, access_token):
        session = self._service.get_session(access_token)
        resp = session.delete('client/%s' % id).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_token(self, client_id, access_token):
        session = self._service.get_session(access_token)
        resp = session.delete('client/%s/tokens' % client_id).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        message = resp.get('message')
        return message

