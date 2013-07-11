from flask import request, session, redirect, make_response, url_for, g
from app import app, db
from app.exceptions import *
from app.oauth import twitter, musicbrainz, CritiqueBrainzAuthorizationProvider
from app.models import User

@app.route('/oauth/authorize/<provider>', methods=['GET'])
def oauth_authorize_handler(provider):
    """ Authorization endpoint. Redirects user to proper authentication
        provider and saves passed data in session for further processing. 
    """
    oauth_provider = CritiqueBrainzAuthorizationProvider()

    # validate arguments
    response_type = request.args.get('response_type')
    if response_type != 'code':
        raise AuthorizationError('unsupported_response_type')
    
    client_id = request.args.get('client_id')
    if oauth_provider.validate_client_id(client_id) is not True:
        raise AuthorizationError('unauthorized_client')

    scope = request.args.get('scope')
    if oauth_provider.validate_scope(client_id, scope) is not True:
        raise AuthorizationError('invalid_scope')

    redirect_uri = request.args.get('redirect_uri')
    if oauth_provider.validate_redirect_uri(client_id, redirect_uri) is not True:
        raise AuthorizationError('invalid_request')

    state = request.args.get('state')

    # save request parameters in session
    session['auth_request'] = dict(response_type=response_type,
        client_id=client_id, scope=scope, state=state, 
        redirect_uri=redirect_uri)

    if provider == 'twitter':
        # prepare twitter authentication
        try:
            request_token, request_token_secret = twitter.get_request_token(
                params=dict(
                    oauth_callback=url_for('oauth_post_login_handler', 
                        provider='twitter', 
                        _external=True)
                    )
                )
            # save request token in session
            session['auth_request'].update(provider='twitter',
                request_token=request_token, 
                request_token_secret=request_token_secret)
        except:
            raise AuthorizationError('server_error')
        else:
            return redirect(twitter.get_authorize_url(request_token))

    elif provider == 'musicbrainz':
        #TODO: MusicBrainz support
        pass
    else:
        raise AbortError('No such authentication provider')

@app.route('/oauth/authorize/<provider>/post_login', methods=['GET'])
def oauth_post_login_handler(provider):
    try:
        # fetch request parameters from session
        auth_request = session['auth_request']
        provider = auth_request['provider']
    except:
        raise AuthorizationError('access_denied')
    else:
        oauth_provider = CritiqueBrainzAuthorizationProvider()

    if provider == 'twitter':
        # check if user denied authentication
        if request.args.get('denied') is not None:
            raise AuthorizationError('access_denied')

        # verify request token
        oauth_token = request.args.get('oauth_token')
        oauth_verifier = request.args.get('oauth_verifier')
        if auth_request['request_token'] != oauth_token:
            raise AuthorizationError('access_denied')

        # open a session and fetch user credentials
        request_token = auth_request['request_token']
        request_token_secret = auth_request['request_token_secret']
        try:
            twitter_session = twitter.get_auth_session(request_token, 
                request_token_secret, method='POST', 
                data={'oauth_verifier': oauth_verifier})
            resp = twitter_session.get('account/verify_credentials.json')
            credentials = resp.json()
        except:
            raise AuthorizationError('server_error')
        twitter_account_id = credentials.get('id_str')
        twitter_display_name = credentials.get('screen_name')

        # user lookup
        user = User.query.filter(User.twitter_id == twitter_account_id).first()
        if user is not None:
            g.user = user
        else:
            # if no user found, create a new one
            user = User(twitter_display_name, '', twitter_account_id)
            db.session.add(user)
            db.session.commit()
            g.user = user

    elif provider == 'musicbrainz':
        #TODO: MusicBrainz support
        pass
    else:
        raise AuthorizationError('server_error')

    try:
        # prepare response
        state = auth_request['state']
        response = oauth_provider.get_authorization_code(
            response_type=auth_request['response_type'],
            client_id=auth_request['client_id'],
            redirect_uri=auth_request['redirect_uri'],
            state=state)
        flask_res = make_response(response.text, response.status_code)
        for k, v in response.headers.iteritems():
            flask_res.headers[k] = v
    except:
        raise AuthorizationError('server_error')
    else:
        return flask_res

@app.route('/oauth/token', methods=['POST'])
def oauth_token_handler():
    #TODO: token redeem
    pass