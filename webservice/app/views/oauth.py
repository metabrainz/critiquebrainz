from flask import request, session, redirect
from app.exceptions import *
from app import app
from app.oauth import twitter, musicbrainz

@app.route('/oauth/authorize/twitter', methods=['GET'])
def oauth_twitter_login():
    global session
    callback = request.args.get('callback')
    if callback is None:
        raise MissingDataError('callback')
    try:    
        request_token, request_token_secret = twitter.get_request_token()
        session['twitter_request_token'] = request_token
        session['twitter_request_token_secret'] = request_token_secret
        session['twitter_callback'] = callback
    except:
        return redirect(callback+'?error=True')
    else:
        return redirect(twitter.get_authorize_url(request_token))
    
@app.route('/oauth/authorize/twitter/post_login', methods=['GET'])
def oauth_twitter_post_login():
    global session
    callback = session['twitter_callback']
    request_token = session['twitter_request_token']
    request_token_secret = session['twitter_request_token_secret']
    oauth_verifier = request.args.get('oauth_verifier')
    
    # fetching access token
    try:
        
        access_token = twitter.get_access_token(request_token, 
            request_token_secret, method='POST', 
            data={'oauth_verifier': oauth_verifier})
        session.clear() # session data clean-up
    except:
        return redirect(callback+'?error=true')
    
    
    session.clear() # session data clean-up
    return redirect(callback+'?user_id=%s' % user.id)
        
@app.route('/all_ok')
def all_ok():
    return 'All ok!'
