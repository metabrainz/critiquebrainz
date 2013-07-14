from flask import request, session, redirect, url_for, g, render_template, flash
from app import app, db, oauth
from app.exceptions import *
from app.oauth import twitter, musicbrainz
from app.models import User, OAuthClient
from functools import wraps

# Authentication
def require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('oauth_login', **request.args))
        else:
            return f(*args, **kwargs)
    return decorated

@app.before_request
def register_global_user():
    if 'user_id' in session:
        g.user = User.query.get(session.get('user_id'))
    else:
        g.user = None

@app.route('/oauth/login', methods=['GET'])
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

# Authorization
@app.route('/oauth/authorize', methods=['GET', 'POST'])
@require_login
@oauth.authorize_handler
def oauth_authorize(*args, **kwargs):
    """ OAuth authorization endpoint. If user is logged in, it prompts
        for authorization. Otherwise, it redirects to login form.
    """
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = OAuthClient.query.filter_by(id=client_id).first()
        kwargs['client'] = client
        print str(kwargs)
        return render_template('oauth/prompt.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'

# Twitter authentication
@app.route('/oauth/login/twitter', methods=['GET'])
def oauth_login_twitter():
    request_token, request_token_secret = twitter.get_request_token(
        params=dict(
            oauth_callback=url_for('oauth_post_login_twitter', 
                _external=True, 
                **request.args)
            )
        )
    session['twitter'] = dict(request_token=request_token,
        request_token_secret=request_token_secret)
    return redirect(twitter.get_authorize_url(request_token))

@app.route('/oauth/login/twitter/post', methods=['GET'])
def oauth_post_login_twitter():

    if 'twitter' not in session:
        return redirect(url_for('oauth_login', next=request.args.get('next', None)))

    # check if user denied authentication
    if 'denied' in request.args:
        flash('You did not authorize the request', 'error')
        return redirect(url_for('oauth_login', next=request.args.get('next', None)))

    # verify request token
    oauth_token = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')
    if session['twitter'].get('request_token', None) != oauth_token:
        return redirect(url_for('oauth_login', next=request.args.get('next', None)))

    # open a session and fetch user credentials
    request_token = session['twitter'].get('request_token', None)
    request_token_secret = session['twitter'].get('request_token_secret', None)
    try:
        twitter_session = twitter.get_auth_session(request_token, 
            request_token_secret, method='POST', 
            data={'oauth_verifier': oauth_verifier})
        resp = twitter_session.get('account/verify_credentials.json')
        credentials = resp.json()
    except:
        flash('Could not fetch data from Twitter servers')
        return redirect(url_for('oauth_login', next=request.args.get('next', None)))

    twitter_id = credentials.get('id_str')
    twitter_display_name = credentials.get('screen_name')

    # user lookup
    user = User.query.filter_by(twitter_id=twitter_id).first()
    if user is not None:
        session['user_id'] = user.id
        g.user = user
    else:
        # if no user found, create a new one
        user = User(display_name=twitter_display_name,
            twitter_id=twitter_id)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        g.user = user

    # redirect to login
    if 'next' in request.args:
        return redirect(request.args.get('next'))
    else:
        return redirect(url_for('oauth_login'))

# MusicBrainz authentication
@app.route('/oauth/authorize/musicbrainz', methods=['GET'])
def oauth_login_musicbrainz():
    pass

@app.route('/oauth/authorize/musicbrainz/post_login', methods=['GET'])
def oauth_post_login_musicbrainz():
    pass