from provider import MusicBrainzAuthentication
from critiquebrainz import app

musicbrainz = MusicBrainzAuthentication(
    name='musicbrainz',
    client_id=app.config['MUSICBRAINZ_CLIENT_ID'],
    client_secret=app.config['MUSICBRAINZ_CLIENT_SECRET'],
    authorize_url='https://musicbrainz.org/oauth2/authorize',
    access_token_url='https://musicbrainz.org/oauth2/token',
    base_url='https://musicbrainz.org/')
