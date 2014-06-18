import json
import requests
from requests.exceptions import ConnectionError
from rauth import OAuth2Service

from flask import url_for

from critiquebrainz.utils import build_url
from critiquebrainz.exceptions import ServerError, ServerUnavailableError


class CritiqueBrainzAPI(object):
    """Provides interface to CritiqueBrainz server."""

    scope = 'user authorization review vote client'

    def __init__(self, base_url, client_id, **kwargs):
        self.base_url = base_url
        self.client_id = client_id
        self._service = OAuth2Service(base_url=base_url,
                                      client_id=client_id,
                                      **kwargs)

    def generate_musicbrainz_authorization_uri(self):
        params = dict(response_type='code',
                      redirect_uri=url_for('login.post', _external=True),
                      scope=self.scope,
                      client_id=self.client_id)
        return build_url(self.base_url + 'login/musicbrainz', params)

    def get_token_from_code(self, code):
        data = dict(grant_type='code',
                    code=code,
                    scope=self.scope,
                    redirect_uri=url_for('login.post', _external=True))
        try:
            resp = self._service.get_raw_access_token(data=data).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        access_token = resp.get('access_token')
        refresh_token = resp.get('refresh_token')
        expires_in = resp.get('expires_in')
        return access_token, refresh_token, expires_in

    def get_token_from_refresh_token(self, refresh_token):
        data = dict(grant_type='refresh_token',
                    refresh_token=refresh_token,
                    scope=self.scope)
        try:
            resp = self._service.get_raw_access_token(data=data).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        access_token = resp.get('access_token')
        refresh_token = resp.get('refresh_token')
        expires_in = resp.get('expires_in')
        return access_token, refresh_token, expires_in

    def get_me(self, access_token, inc=[]):
        params = dict(inc=' '.join(inc))
        try:
            session = self._service.get_session(access_token)
            resp = session.get('user/me', params=params).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        me = resp.get('user')
        return me

    def validate_oauth_request(self, client_id, response_type, redirect_uri, scope):
        data = dict(client_id=client_id,
                    response_type=response_type,
                    redirect_uri=redirect_uri,
                    scope=scope)
        try:
            resp = requests.post(self.base_url + 'oauth/validate', data=data).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        client = resp.get('client')
        return client

    def authorize(self, client_id, response_type, redirect_uri, scope, access_token):
        data = dict(client_id=client_id,
                    response_type=response_type,
                    redirect_uri=redirect_uri,
                    scope=scope)
        try:
            session = self._service.get_session(access_token)
            resp = session.post('oauth/authorize', data=data).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        code = resp.get('code')
        return code

    def get_review(self, id, inc=[]):
        params = dict(inc=' '.join(inc))
        try:
            resp = requests.get(self.base_url + 'review/%s' % id, params=params).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        review = resp.get('review')
        return review

    def get_me_reviews(self, sort, limit, offset, access_token):
        params = dict(sort=sort, limit=limit, offset=offset)
        try:
            session = self._service.get_session(access_token)
            resp = session.get('user/me/reviews', params=params).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        count = resp.get('count')
        reviews = resp.get('reviews')
        return count, reviews

    def get_reviews(self, release_group=None, user_id=None, sort=None, limit=None, offset=None, inc=[]):
        params = dict(release_group=release_group,
                      user_id=user_id, sort=sort, limit=limit, offset=offset, inc=' '.join(inc))
        try:
            resp = requests.get(self.base_url + 'review/', params=params).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        count = resp.get('count')
        reviews = resp.get('reviews')
        return count, reviews

    def get_me_clients(self, access_token):
        try:
            session = self._service.get_session(access_token)
            resp = session.get('user/me/clients').json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        clients = resp.get('clients')
        return clients

    def get_me_tokens(self, access_token):
        try:
            session = self._service.get_session(access_token)
            resp = session.get('user/me/tokens').json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        tokens = resp.get('tokens')
        return tokens

    def get_client(self, id, access_token):
        try:
            session = self._service.get_session(access_token)
            resp = session.get('client/%s' % id).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        client = resp.get('client')
        return client

    def get_vote(self, review_id, access_token):
        try:
            session = self._service.get_session(access_token)
            resp = session.get('review/%s/vote' % review_id).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        vote = resp.get('vote')
        return vote

    def get_user(self, user_id, inc=[]):
        params = dict(inc=' '.join(inc))
        try:
            resp = requests.get(self.base_url + 'user/%s' % user_id, params=params).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        user = resp.get('user')
        return user

    def get_users(self, limit=None, offset=None):
        params = dict(limit=limit, offset=offset)
        try:
            resp = requests.get(self.base_url + 'user/', params=params).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        count = resp.get('count')
        users = resp.get('users')
        return count, users

    def get_review_languages(self):
        try:
            resp = requests.get(self.base_url + 'review/languages').json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        return resp.get('languages')

    def create_client(self, name, desc, website, redirect_uri, scopes, access_token):
        data = dict(name=name,
                    desc=desc,
                    website=website,
                    redirect_uri=redirect_uri,
                    scopes=scopes)
        headers = {'Content-type': 'application/json'}
        try:
            session = self._service.get_session(access_token)
            resp = session.post('client/', data=json.dumps(data), headers=headers).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        client = resp.get('client')
        client_id = client.get('id')
        client_secret = client.get('secret')
        return message, client_id, client_secret

    def create_review(self, release_group, text, license_choice, language, access_token):
        data = dict(release_group=release_group, text=text, license_choice=license_choice, language=language)
        headers = {'Content-type': 'application/json'}
        try:
            session = self._service.get_session(access_token)
            resp = session.post('review/', data=json.dumps(data), headers=headers).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        return resp.get('message'), resp.get('id')

    def update_review(self, id, access_token, **kwargs):
        data = kwargs
        headers = {'Content-type': 'application/json'}
        try:
            session = self._service.get_session(access_token)
            resp = session.post('review/%s' % id, data=json.dumps(data), headers=headers).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def update_profile(self, access_token, **kwargs):
        data = kwargs
        headers = {'Content-type': 'application/json'}
        try:
            session = self._service.get_session(access_token)
            resp = session.post('user/me', data=json.dumps(data), headers=headers).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def update_client(self, id, access_token, **kwargs):
        data = kwargs
        headers = {'Content-type': 'application/json'}
        try:
            session = self._service.get_session(access_token)
            resp = session.post('client/%s' % id, data=json.dumps(data), headers=headers).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def update_review_vote(self, review_id, access_token, **kwargs):
        data = kwargs
        headers = {'Content-type': 'application/json'}
        try:
            session = self._service.get_session(access_token)
            resp = session.put('review/%s/vote' % review_id, data=json.dumps(data), headers=headers).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_review(self, id, access_token):
        try:
            session = self._service.get_session(access_token)
            resp = session.delete('review/%s' % id).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_review_vote(self, review_id, access_token):
        try:
            session = self._service.get_session(access_token)
            resp = session.delete('review/%s/vote' % review_id).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_profile(self, access_token):
        try:
            session = self._service.get_session(access_token)
            resp = session.delete('user/me').json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_client(self, id, access_token):
        try:
            session = self._service.get_session(access_token)
            resp = session.delete('client/%s' % id).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_token(self, client_id, access_token):
        try:
            session = self._service.get_session(access_token)
            resp = session.delete('client/%s/tokens' % client_id).json()
        except ConnectionError:
            raise ServerUnavailableError()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

