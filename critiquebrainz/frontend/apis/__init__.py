from flask import current_app
from critiquebrainz import __version__
from musicbrainz.musicbrainz import MusicBrainzClient
from mbspotify import MBSpotifyClient
from spotify import SpotifyClient


musicbrainz = MusicBrainzClient()
musicbrainz.init_app("CritiqueBrainz Client", __version__)

mbspotify = MBSpotifyClient(current_app.config['MBSPOTIFY_BASE_URI'])

spotify = SpotifyClient()
