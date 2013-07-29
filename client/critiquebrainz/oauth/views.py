from flask import Blueprint, request, redirect, render_template, url_for, session
from flask.ext.login import login_required, current_user
from critiquebrainz.exceptions import OAuthError
from critiquebrainz.api import api
from critiquebrainz.utils import build_url

bp = Blueprint('oauth', __name__)

@bp.route('/authorize', methods=['GET', 'POST'], endpoint='authorize_prompt')
@login_required
def oauth_authorize_prompt_handler():
    client_id = request.args.get('client_id')
    response_type = request.args.get('response_type')
    redirect_uri = request.args.get('redirect_uri')
    scope = request.args.get('scope')
    state = request.args.get('state')
    if request.method == 'POST':
        error, code = api.authorize(client_id, response_type, redirect_uri, scope, current_user.access_token)
        if error:
            raise OAuthError(error)
        else:
            return redirect(build_url(redirect_uri, dict(code=code, state=state)))
    if request.method == 'GET':
        error, client = api.get_client(client_id, response_type, redirect_uri, scope)
        if error is not None:
            raise OAuthError(error)
        return render_template('oauth/prompt.html', client=client, scope=scope, 
            cancel_url=build_url(redirect_uri, dict(error='access_denied')))
