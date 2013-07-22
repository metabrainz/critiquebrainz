from flask import Blueprint, request, url_for, render_template
from flask.ext.login import login_required
from critiquebrainz.db import db, OAuthClient
from . import oauth as oauth_provider

oauth = Blueprint('oauth', __name__, url_prefix='/oauth')

@oauth.route('/authorize', methods=['GET', 'POST'])
@oauth_provider.authorize_handler
@login_required
def oauth_authorize(*args, **kwargs):
    client_id = kwargs.get('client_id')
    client = OAuthClient.query.filter_by(client_id=client_id).first()
    if request.method == 'GET':
        kwargs['client'] = client
        return render_template('oauth/prompt.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'

@oauth.route('/token', methods=['POST'])
@oauth_provider.token_handler
def oauth_token():
    pass

@oauth.route('/errors', methods=['GET'])
def oauth_errors():
    reasons = {'server_error': 'The authorization server encountered an '\
                               'unexpected condition that prevented it from '\
                               'fulfilling the request.',
               'invalid_scope': 'The requested scope is invalid, unknown, '\
                                'or malformed.',
               'access_denied': 'The resource owner or authorization '\
                                'server denied the request.',
               'invalid_client_id': 'Invalid client id.',
               'mismatching_redirect_uri': 'Mismatching redirect uri.',
               'missing_redirect_uri': 'Missing redirect uri.',
               'invalid_redirect_uri': 'Invalid redirect uri.'}
    error = request.args.get('error') or 'server_error'
    return render_template('oauth/error.html', reason=reasons.get(error, None))