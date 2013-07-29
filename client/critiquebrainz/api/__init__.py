from critiquebrainz import app
from api import CritiqueBrainzAPI

api = CritiqueBrainzAPI(
    name='critiquebrainz',
    client_id=app.config['CRITIQUEBRAINZ_CLIENT_ID'],
    client_secret=app.config['CRITIQUEBRAINZ_CLIENT_SECRET'],
    authorize_url='',
    access_token_url=app.config['CRITIQUEBRAINZ_BASE_URI']+'oauth/token',
    base_url=app.config['CRITIQUEBRAINZ_BASE_URI'])
