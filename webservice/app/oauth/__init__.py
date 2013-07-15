from authentication import TwitterAuthentication
from authorization import AuthProvider
from app import app

twitter = TwitterAuthentication(
    consumer_key=app.config['TWITTER_CONSUMER_KEY'],
    consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
    name='twitter',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    request_token_url='https://api.twitter.com/oauth/request_token',
    base_url='https://api.twitter.com/1.1/')

"""  
musicbrainz = OAuth2Service(
    client_id=app.config['MUSICBRAINZ_CLIENT_ID'],
    client_secret=app.config['MUSICBRAINZ_CLIENT_SECRET'],
    name='musicbrainz',
    authorize_url='https://musicbrainz.org/oauth2/authorize',
    access_token_url='https://musicbrainz.org/oauth2/token',
    base_url='https://musicbrainz.org/')"""