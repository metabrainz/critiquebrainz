from .. import oauth
from critiquebrainz import app
from flask import session

musicbrainz = oauth.remote_app(
    'musicbrainz',
    request_token_params={'scope': 'profile'},
    consumer_key=app.config['MUSICBRAINZ_CLIENT_ID'],
    consumer_secret=app.config['MUSICBRAINZ_CLIENT_SECRET'],
    request_token_url=None,
    authorize_url='https://musicbrainz.org/oauth2/authorize',
    access_token_url='https://musicbrainz.org/oauth2/token',
    access_token_method='POST',
    base_url='https://musicbrainz.org/',
)

@musicbrainz.tokengetter
def get_musicbrainz_token():
    return session.get('musicbrainz_token')