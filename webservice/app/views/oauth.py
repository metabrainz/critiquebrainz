from flask import request, session, redirect, url_for, g, render_template, flash
from app import app, db, oauth
from app.exceptions import *
from app.oauth import twitter, musicbrainz
from app.models import User, OAuthClient
from functools import wraps

# Other
def require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('oauth_login', next=request.url, 
                provider=request.args.get('provider', None)))
        else:
            return f(*args, **kwargs)
    return decorated

@app.before_request
def register_global_user():
    if 'user_id' in session:
        g.user = User.query.get(session.get('user_id'))
    else:
        g.user = None

# Authentication
@app.route('/oauth/login', methods=['GET'])
@twitter.error_handler
@musicbrainz.error_handler
def oauth_login():
    """ Login endpoint. If a `provider` argument is specified in uri query,
        it will automaticaly redirect to the relevant authentication
        provider (Twitter or MusicBrainz). 
    """
    provider = request.args.get('provider', None)
    if provider == 'twitter':
        return redirect(url_for('oauth_login_twitter', **request.args))
    elif provider == 'musicbrainz':
        return redirect(url_for('oauth_login_musicbrainz', **request.args))
    else:
        return render_template('oauth/login.html')

@app.route('/oauth/logout', methods=['GET'])
@require_login
def oauth_logout():
    del session['user_id']
    flash('Successfully logged out', 'success')
    return redirect(url_for('oauth_login', next=request.args.get('next', None)))

# Twitter authentication
@app.route('/oauth/login/twitter', methods=['GET'])
@twitter.login_handler
def oauth_login_twitter():
    pass

@app.route('/oauth/login/twitter/post', methods=['GET'])
@twitter.post_login_handler
def oauth_post_login_twitter():
    return 'Now we have nowhere to go to'

# MusicBrainz authentication
@app.route('/oauth/login/musicbrainz', methods=['GET'])
@musicbrainz.login_handler
def oauth_login_musicbrainz():
    pass

@app.route('/oauth/login/musicbrainz/post', methods=['GET'])
@musicbrainz.post_login_handler
def oauth_post_login_musicbrainz():
    return 'Now we have nowhere to go to'

# Authorization
@app.route('/oauth/authorize', methods=['GET', 'POST'])
@require_login
@oauth.authorize_handler
def oauth_authorize(*args, **kwargs):
    """ OAuth authorization endpoint. If user is logged in, it prompts
        for authorization. Otherwise, it redirects to login form.
    """
    client_id = kwargs.get('client_id')
    client = OAuthClient.query.filter_by(client_id=client_id).first()
    if request.method == 'GET':
        kwargs['client'] = client
        return render_template('oauth/prompt.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'

@app.route('/oauth/token', methods=['POST'])
@oauth.token_handler
def access_token():
    return None