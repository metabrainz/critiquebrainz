from flask import Blueprint, render_template, redirect, request
from werkzeug.exceptions import BadRequest
from critiquebrainz.ws.oauth.exceptions import OAuthError
from flask_login import login_required, current_user

import critiquebrainz.db.oauth_client as db_oauth_client
from critiquebrainz.utils import build_url
from critiquebrainz.ws.oauth import oauth

oauth_bp = Blueprint('oauth', __name__)


@oauth_bp.route('/authorize', methods=['GET', 'POST'])
@login_required
def authorize_prompt():
    """OAuth 2.0 authorization endpoint."""
    response_type = request.args.get('response_type')
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    scope = request.args.get('scope')
    state = request.args.get('state')

    if request.method == 'GET':  # Client requests access
        try:
            oauth.validate_authorization_request(client_id, response_type, redirect_uri, scope)
            client = db_oauth_client.get_client(client_id)
            return render_template('oauth/prompt.html', client=client, scope=scope,
                                cancel_url=build_url(redirect_uri, dict(error='access_denied')))
        except OAuthError as e:
            raise BadRequest(e.desc)

    if request.method == 'POST':  # User grants access to the client
        try:
            oauth.validate_authorization_request(client_id, response_type, redirect_uri, scope)
            code = oauth.generate_grant(client_id, current_user.id, redirect_uri, scope)
            return redirect(build_url(redirect_uri, dict(code=code, state=state)))
        except OAuthError as e:
            raise BadRequest(e.desc)
