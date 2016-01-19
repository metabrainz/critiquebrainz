from flask import Blueprint, render_template, redirect, request
from flask_login import login_required, current_user

from critiquebrainz.utils import build_url
from critiquebrainz.ws.oauth import oauth
from critiquebrainz.data.model.oauth_client import OAuthClient

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
        oauth.validate_authorization_request(client_id, response_type, redirect_uri, scope)
        client = OAuthClient.query.get(client_id)
        return render_template('oauth/prompt.html', client=client, scope=scope,
                               cancel_url=build_url(redirect_uri, dict(error='access_denied')))

    if request.method == 'POST':  # User grants access to the client
        oauth.validate_authorization_request(client_id, response_type, redirect_uri, scope)
        code = oauth.generate_grant(client_id, current_user.id, redirect_uri, scope)
        return redirect(build_url(redirect_uri, dict(code=code, state=state)))
