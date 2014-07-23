from flask import Blueprint, request, redirect, render_template
from flask.ext.login import login_required, current_user
from critiquebrainz.apis import server
from critiquebrainz.utils import build_url

oauth_bp = Blueprint('oauth', __name__)


@oauth_bp.route('/authorize', methods=['GET', 'POST'], endpoint='authorize_prompt')
@login_required
def oauth_authorize_prompt_handler():
    """OAuth 2.0 authorization endpoint."""
    response_type = request.args.get('response_type')
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    scope = request.args.get('scope')
    state = request.args.get('state')

    if request.method == 'GET':  # Client requests access
        client = server.validate_oauth_request(client_id, response_type, redirect_uri, scope)
        return render_template('oauth/prompt.html', client=client, scope=scope,
                               cancel_url=build_url(redirect_uri, dict(error='access_denied')))

    if request.method == 'POST':  # User grants access to the client
        code = server.authorize(client_id, response_type, redirect_uri, scope, current_user.access_token)
        return redirect(build_url(redirect_uri, dict(code=code, state=state)))
