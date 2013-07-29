from provider import TwitterAuthentication, MusicBrainzAuthentication
from critiquebrainz import app

twitter = TwitterAuthentication(
	name='twitter',
    consumer_key=app.config['TWITTER_CONSUMER_KEY'],
    consumer_secret=app.config['TWITTER_CONSUMER_SECRET'],
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    base_url='https://api.twitter.com/1.1/')

musicbrainz = MusicBrainzAuthentication(
	name='musicbrainz',
    client_id=app.config['MUSICBRAINZ_CLIENT_ID'],
    client_secret=app.config['MUSICBRAINZ_CLIENT_SECRET'],
    authorize_url='https://musicbrainz.org/oauth2/authorize',
    access_token_url='https://musicbrainz.org/oauth2/token',
    base_url='https://musicbrainz.org/')
