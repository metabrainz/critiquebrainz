from critiquebrainz import app, app_name, app_version

from server import CritiqueBrainzAPI
server = CritiqueBrainzAPI(
    name='critiquebrainz',
    client_id=app.config['CRITIQUEBRAINZ_CLIENT_ID'],
    client_secret=app.config['CRITIQUEBRAINZ_CLIENT_SECRET'],
    authorize_url='',
    access_token_url=app.config['CRITIQUEBRAINZ_BASE_URI'] + 'oauth/token',
    base_url=app.config['CRITIQUEBRAINZ_BASE_URI'])

from musicbrainz.musicbrainz import MusicBrainzClient
musicbrainz = MusicBrainzClient()
musicbrainz.init_app(app, app_name, app_version)

from mbspotify import MBSpotifyClient
mbspotify = MBSpotifyClient(app.config['MBSPOTIFY_BASE_URI'])

from spotify import SpotifyClient
spotify = SpotifyClient()