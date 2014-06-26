import json
import requests
from rauth import OAuth2Service
from requests.exceptions import ConnectionError

from flask import url_for

from critiquebrainz.utils import build_url
from critiquebrainz.exceptions import ServerError


class CritiqueBrainzAPI(object):
    """Provides interface to CritiqueBrainz server."""

    scope = 'user authorization review vote client'

    def __init__(self, base_url, client_id, **kwargs):
        self.base_url = base_url
        self.client_id = client_id
        self._service = OAuth2Service(base_url=base_url, client_id=client_id, **kwargs)

    def generate_musicbrainz_authorization_uri(self):
        params = dict(response_type='code',
                      redirect_uri=url_for('login.post', _external=True),
                      scope=self.scope,
                      client_id=self.client_id)
        return build_url(self.base_url + 'login/musicbrainz', params)

    def get_token_from_auth_code(self, code):
        data = dict(grant_type='authorization_code',
                    code=code,
                    scope=self.scope,
                    redirect_uri=url_for('login.post', _external=True))
        resp = self._service.get_raw_access_token(data=data).json()
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
        resp = self._service.get_raw_access_token(data=data).json()
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
        session = self._service.get_session(access_token)
        resp = session.get('user/me', params=params).json()
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
        resp = requests.post(self.base_url + 'oauth/validate', data=data).json()
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
        session = self._service.get_session(access_token)
        resp = session.post('oauth/authorize', data=data).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        code = resp.get('code')
        return code

    def get_review(self, id, inc=[]):
        params = dict(inc=' '.join(inc))
        resp = requests.get(self.base_url + 'review/%s' % id, params=params).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        review = resp.get('review')
        return review

    def get_me_reviews(self, sort, limit, offset, access_token):
        params = dict(sort=sort, limit=limit, offset=offset)
        session = self._service.get_session(access_token)
        resp = session.get('user/me/reviews', params=params).json()
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
        resp = requests.get(self.base_url + 'review/', params=params).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        count = resp.get('count')
        reviews = resp.get('reviews')
        return count, reviews

    def get_me_applications(self, access_token):
        session = self._service.get_session(access_token)
        resp = session.get('user/me/applications').json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        return resp.get('applications')

    def get_me_tokens(self, access_token):
        session = self._service.get_session(access_token)
        resp = session.get('user/me/tokens').json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        tokens = resp.get('tokens')
        return tokens

    def get_application(self, id, access_token):
        session = self._service.get_session(access_token)
        resp = session.get('application/%s' % id).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        application = resp.get('application')
        return application

    def get_vote(self, review_id, access_token):
        session = self._service.get_session(access_token)
        resp = session.get('review/%s/vote' % review_id).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        vote = resp.get('vote')
        return vote

    def get_user(self, user_id, inc=[]):
        params = dict(inc=' '.join(inc))
        resp = requests.get(self.base_url + 'user/%s' % user_id, params=params).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        user = resp.get('user')
        return user

    def get_users(self, limit=None, offset=None):
        params = dict(limit=limit, offset=offset)
        resp = requests.get(self.base_url + 'user/', params=params).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        count = resp.get('count')
        users = resp.get('users')
        return count, users

    def get_review_languages(self):
        resp = requests.get(self.base_url + 'review/languages').json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        return resp.get('languages')

    def create_application(self, name, desc, website, redirect_uri, access_token):
        data = dict(name=name,
                    desc=desc,
                    website=website,
                    redirect_uri=redirect_uri)
        headers = {'Content-type': 'application/json'}
        session = self._service.get_session(access_token)
        resp = session.post('application/', data=json.dumps(data), headers=headers).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        application = resp.get('application')
        client_id = application.get('id')
        client_secret = application.get('secret')
        return message, client_id, client_secret

    def create_review(self, release_group, text, license_choice, language, access_token):
        data = dict(release_group=release_group, text=text, license_choice=license_choice, language=language)
        headers = {'Content-type': 'application/json'}
        session = self._service.get_session(access_token)
        resp = session.post('review/', data=json.dumps(data), headers=headers).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        return resp.get('message'), resp.get('id')

    def update_review(self, id, access_token, **kwargs):
        data = kwargs
        headers = {'Content-type': 'application/json'}
        session = self._service.get_session(access_token)
        resp = session.post('review/%s' % id, data=json.dumps(data), headers=headers).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def update_profile(self, access_token, **kwargs):
        data = kwargs
        headers = {'Content-type': 'application/json'}
        session = self._service.get_session(access_token)
        resp = session.post('user/me', data=json.dumps(data), headers=headers).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def update_application(self, id, access_token, **kwargs):
        data = kwargs
        headers = {'Content-type': 'application/json'}
        session = self._service.get_session(access_token)
        resp = session.post('application/%s' % id, data=json.dumps(data), headers=headers).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def update_review_vote(self, review_id, access_token, **kwargs):
        data = kwargs
        headers = {'Content-type': 'application/json'}
        session = self._service.get_session(access_token)
        resp = session.put('review/%s/vote' % review_id, data=json.dumps(data), headers=headers).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_review(self, id, access_token):
        session = self._service.get_session(access_token)
        resp = session.delete('review/%s' % id).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_review_vote(self, review_id, access_token):
        session = self._service.get_session(access_token)
        resp = session.delete('review/%s/vote' % review_id).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def spam_report_review(self, review_id, access_token):
        session = self._service.get_session(access_token)
        resp = session.post('review/%s/report' % review_id).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_profile(self, access_token):
        session = self._service.get_session(access_token)
        resp = session.delete('user/me').json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_application(self, id, access_token):
        session = self._service.get_session(access_token)
        resp = session.delete('application/%s' % id).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

    def delete_token(self, client_id, access_token):
        session = self._service.get_session(access_token)
        resp = session.delete('application/%s/tokens' % client_id).json()
        error = resp.get('error')
        if error:
            desc = resp.get('description')
            raise ServerError(code=error, desc=desc)
        message = resp.get('message')
        return message

