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
                      scope='user authorization publication',
                      client_id=self.client_id)
        return build_url(self.base_url+'login/twitter', params)

    def generate_musicbrainz_authorization_uri(self):
        params = dict(response_type='code',
                      redirect_uri=url_for('login.post', _external=True),
                      scope='user authorization publication',
                      client_id=self.client_id)
        return build_url(self.base_url+'login/musicbrainz', params)

    def get_token_from_code(self, code):
        data = dict(grant_type='code',
                    code=code,
                    scope='user authorization publication',
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
                    scope='user authorization publication')
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

    def get_client(self, client_id, response_type, redirect_uri, scope):
        data = dict(client_id=client_id,
                    response_type=response_type,
                    redirect_uri=redirect_uri,
                    scope=scope)
        resp = requests.post(self.base_url+'oauth/client', data=data).json()
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

    def get_me_publications(self, access_token):
        session = self._service.get_session(access_token)
        resp = session.get('user/me', params=dict(inc='publications')).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise APIError(code=error, desc=desc)
        me = resp.get('user')
        return me

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

    def update_publication(self, id, text, access_token):
        session = self._service.get_session(access_token)
        data = dict(text=text)
        headers = {'Content-type': 'application/json'}
        resp = session.put('publication/%s' % id, data=json.dumps(data), headers=headers).json()
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
