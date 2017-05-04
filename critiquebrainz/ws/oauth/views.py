from flask import Blueprint, request, jsonify
from critiquebrainz.ws.oauth import oauth
from critiquebrainz.ws.oauth.exceptions import UnsupportedGrantType
from critiquebrainz.decorators import nocache, crossdomain

oauth_bp = Blueprint('ws_oauth', __name__)


@oauth_bp.route('/token', methods=['POST'])
@nocache
@crossdomain()
def oauth_token_handler():
    """OAuth 2.0 token endpoint.

    :form string client_id:
    :form string client_secret:
    :form string redirect_uri:
    :form string grant_type: ``authorization_code`` or ``refresh_token``
    :form string code: (not required if grant_type is ``refresh_token``)
    :form string refresh_token: (not required if grant_type is ``authorization_code``)

    :resheader Content-Type: *application/json*
    """
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    redirect_uri = request.form.get('redirect_uri')
    grant_type = request.form.get('grant_type')
    code = request.form.get('code')
    refresh_token = request.form.get('refresh_token')

    oauth.validate_token_request(grant_type, client_id, client_secret, redirect_uri, code, refresh_token)

    if grant_type == 'authorization_code':
        grant = oauth.fetch_grant(client_id, code)
        user_id = grant['user_id']
        scope = grant['scopes']
    elif grant_type == 'refresh_token':
        token = oauth.fetch_token(client_id, refresh_token)
        user_id = token['user_id']
        scope = token['scopes']
    else:
        raise UnsupportedGrantType("Specified grant_type is unsupported. Please, use authorization_code or refresh_token.")

    # Deleting grant and/or existing token(s)
    # TODO(roman): Check if that's necessary:
    oauth.discard_grant(client_id, code)
    oauth.discard_client_user_tokens(client_id, user_id)

    access_token, token_type, expires_in, refresh_token = oauth.generate_token(client_id, refresh_token, user_id, scope)

    return jsonify(dict(access_token=access_token,
                        token_type=token_type,
                        expires_in=expires_in,
                        refresh_token=refresh_token))
