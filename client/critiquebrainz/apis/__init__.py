from flask import current_app
from critiquebrainz import __version__

from server import CritiqueBrainzAPI
server = CritiqueBrainzAPI(
    name='critiquebrainz',
    client_id=current_app.config['CRITIQUEBRAINZ_CLIENT_ID'],
    client_secret=current_app.config['CRITIQUEBRAINZ_CLIENT_SECRET'],
    authorize_url='',  # TODO: Figure out why this argument is empty.
    access_token_url=current_app.config['CRITIQUEBRAINZ_BASE_URI'] + 'oauth/token',
    base_url=current_app.config['CRITIQUEBRAINZ_BASE_URI'])

from musicbrainz.musicbrainz import MusicBrainzClient
musicbrainz = MusicBrainzClient()
musicbrainz.init_app(current_app, "CritiqueBrainz Client", __version__)

from mbspotify import MBSpotifyClient
mbspotify = MBSpotifyClient(current_app.config['MBSPOTIFY_BASE_URI'])

from spotify import SpotifyClient
spotify = SpotifyClient()