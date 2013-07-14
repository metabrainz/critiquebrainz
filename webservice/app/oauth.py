from flask import g
from rauth import OAuth1Service, OAuth2Service
from datetime import datetime, timedelta
from app import app, db, oauth
from app.models import OAuthClient, OAuthGrant, OAuthToken

# authentication providers

twitter = OAuth1Service(
    consumer_key=app.config['TWITTER_CONSUMER_KEY'],
    consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
    name='twitter',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    request_token_url='https://api.twitter.com/oauth/request_token',
    base_url='https://api.twitter.com/1.1/')
    
musicbrainz = OAuth2Service(
    client_id=app.config['MUSICBRAINZ_CLIENT_ID'],
    client_secret=app.config['MUSICBRAINZ_CLIENT_SECRET'],
    name='musicbrainz',
    authorize_url='https://musicbrainz.org/oauth2/authorize',
    access_token_url='https://musicbrainz.org/oauth2/token',
    base_url='https://musicbrainz.org/')

# authorization provider

@oauth.clientgetter
def load_client(client_id):
    return OAuthClient.query.filter_by(id=client_id).first()
    
@oauth.grantgetter
def load_grant(client_id, code):
    return OAuthGrant.query.filter_by(client_id=client_id, code=code).first()
    
@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    # grant expires after 100 seconds
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = OAuthGrant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user=g.user,
        expires=expires
    )
    db.session.add(grant)
    db.session.commit()
    return grant

@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return OAuthToken.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return OAuthToken.query.filter_by(refresh_token=refresh_token).first()

@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    toks = OAuthToken.query.filter_by(client_id=request.client.client_id,
                                      user_id=request.user.id)
    # make sure that every client has only one token connected to a user
    db.session.delete(toks)

    expires_in = token.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    tok = OAuthToken(**token)
    tok.expires = expires
    tok.client_id = request.client.client_id
    tok.user_id = request.user.id
    db.session.add(tok)
    db.session.commit()
    return tok
