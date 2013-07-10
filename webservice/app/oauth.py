from rauth import OAuth1Service, OAuth2Service
from pyoauth2.provider import AuthorizationProvider
from app import app

# authentication providers

twitter = OAuth1Service(
    consumer_key=app.config['TWITTER_CONSUMER_KEY'],
    consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
    name='twitter',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    request_token_url='https://api.twitter.com/oauth/request_token',
    base_url='https://api.twitter.com/1/')
    
musicbrainz = OAuth2Service(
    client_id='gn_M5vKGjZDw55CiRpCKvA',
    client_secret='QVyZm7oXIbfIx5_e-S9ZyQ',
    name='musicbrainz',
    authorize_url='https://musicbrainz.org/oauth2/authorize',
    access_token_url='https://musicbrainz.org/oauth2/token',
    base_url='https://musicbrainz.org/')

