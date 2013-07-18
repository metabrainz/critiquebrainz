from flask import request, session, redirect, url_for, g, render_template, flash
from app import app, db, oauth
from app.exceptions import *
from app.oauth import twitter, musicbrainz
from app.models import User, OAuthClient
from app.utils import append_params_to_url
from functools import wraps

# Authorization
@app.route('/oauth/authorize/<provider>', methods=['GET', 'POST'])
@oauth.authorize_handler
@twitter.authorize_handler
@musicbrainz.authorize_handler
def oauth_authorize(provider, *args, **kwargs):
    """ OAuth authorization endpoint. If user is logged in, it prompts
        for authorization. Otherwise, it redirects to login form.
    """
    if hasattr(g, 'user') is False:
        raise AuthorizationError('server_error')
    client_id = kwargs.get('client_id')
    client = OAuthClient.query.filter_by(client_id=client_id).first()
    if request.method == 'GET':
        kwargs['client'] = client
        return render_template('oauth/prompt.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'

@app.route('/oauth/token', methods=['POST'])
@oauth.token_handler
def oauth_token():
    pass

@app.route('/oauth/errors', methods=['GET'])
def oauth_errors():
    # ugly way to handle errors from the oauthlib package.
    # thankfully, we only need to show them to user, without
    # performing any redirections.
    #TODO: rewrite oauth validator to manage exceptions better
    error = request.args.get('error')
    raise AuthorizationError(error)

@app.errorhandler(AuthorizationError)
def handle_authorization_error(error):
    if error.redirect_uri is not None:
        return redirect(append_params_to_url(error.redirect_uri, error=error.error))
    else:
        return render_template('oauth/error.html', error=error)

# Twitter authentication
@app.route('/oauth/authorize/twitter/post', methods=['GET'])
@twitter.post_login_handler
def oauth_post_login_twitter():
    pass

# MusicBrainz authentication
@app.route('/oauth/authorize/musicbrainz/post', methods=['GET'])
@musicbrainz.post_login_handler
def oauth_post_login_musicbrainz():
    pass
