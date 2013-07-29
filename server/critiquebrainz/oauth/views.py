from flask import Blueprint, request, jsonify
from critiquebrainz.oauth import oauth
from critiquebrainz.exceptions import OAuthError
from critiquebrainz.db import OAuthClient
from critiquebrainz.decorators import nocache

bp = Blueprint('oauth', __name__)

@bp.route('/authorize', methods=['POST'], endpoint='authorize')
@oauth.require_auth('authorization')
@nocache
def oauth_authorize_handler(user):
    client_id = request.form.get('client_id')
    response_type = request.form.get('response_type')
    redirect_uri = request.form.get('redirect_uri')
    scope = request.form.get('scope')

    # validate request
    valid, error = oauth.validate_authorization_request(client_id, response_type, redirect_uri, scope)
    if valid is False:
        raise OAuthError(error)

    # generate new grant
    (code, ) = oauth.generate_grant(client_id, scope, redirect_uri, user.id)
    
    return jsonify(dict(code=code))

@bp.route('/token', methods=['POST'], endpoint='token')
@nocache
def oauth_token_handler():
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    grant_type = request.form.get('grant_type')
    code = request.form.get('code')
    refresh_token = request.form.get('refresh_token')
    redirect_uri = request.form.get('redirect_uri')
    scope = request.form.get('scope')

    # validate request
    valid, error = oauth.validate_token_request(client_id, client_secret, grant_type, scope, code, refresh_token, redirect_uri)
    if valid is False:
        raise OAuthError(error)

    if grant_type == 'code':
        user_id = oauth.fetch_grant(client_id, code).user.id
    elif grant_type == 'refresh_token':
        user_id = oauth.fetch_token(client_id, refresh_token).user.id

    # delete grant and/or existing token(s)
    oauth.discard_grant(client_id, code)
    oauth.discard_client_user_tokens(client_id, user_id)

    # generate new token
    (access_token, token_type, expires_in, refresh_token, scope) = oauth.generate_token(client_id, scope, refresh_token, user_id)
    
    return jsonify(dict(access_token=access_token,
                        token_type=token_type,
                        expires_in=expires_in,
                        refresh_token=refresh_token,
                        scope=scope))

@bp.route('/client', methods=['POST'], endpoint='client')
@nocache
def oauth_client_handler():
    client_id = request.form.get('client_id')
    response_type = request.form.get('response_type')
    redirect_uri = request.form.get('redirect_uri')
    scope = request.form.get('scope')

    # validate request
    valid, error = oauth.validate_authorization_request(client_id, response_type, redirect_uri, scope)
    if valid is False:
        raise OAuthError(error)

    client = OAuthClient.query.get(client_id)

    return jsonify(dict(client=dict(client_id=client.client_id,
                                    name=client.name,
                                    desc=client.desc,
                                    website=client.website)))

@bp.errorhandler(OAuthError)
def oauth_error_handler(error):
    return jsonify(dict(error=error.code)), error.status

@bp.errorhandler(Exception)
def exception_handler(error):
    return oauth_error_handler(OAuthError('server_error'))
