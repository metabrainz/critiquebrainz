from provider import MusicBrainzAuthentication


def init_oauth_providers(app):
    global musicbrainz
    musicbrainz = MusicBrainzAuthentication(
        name='musicbrainz',
        client_id=app.config['MUSICBRAINZ_CLIENT_ID'],
        client_secret=app.config['MUSICBRAINZ_CLIENT_SECRET'],
        authorize_url='https://musicbrainz.org/oauth2/authorize',
        access_token_url='https://musicbrainz.org/oauth2/token',
        base_url='https://musicbrainz.org/')
