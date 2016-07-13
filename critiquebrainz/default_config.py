# DEFAULT CONFIGURATION

DEBUG = False
SECRET_KEY = "CHANGE_THIS"

SQLALCHEMY_DATABASE_URI = "postgresql://critiquebrainz:critiquebrainz@db:5432/critiquebrainz"
TEST_SQLALCHEMY_DATABASE_URI = "postgresql://cb_test:cb_test@db:5432/cb_test"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# CritiqueBrainz OAuth configuration
OAUTH_TOKEN_LENGTH = 40
OAUTH_GRANT_EXPIRE = 60
OAUTH_TOKEN_EXPIRE = 3600

# Redis
REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_NAMESPACE = "CB"

# Mail server
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_FROM_ADDR = "no-reply@critiquebrainz.org"

# List of supported UI languages.
# Valid language codes can be obtained from Transifex.
SUPPORTED_LANGUAGES = [
    'en',  # English
    'hr',  # Croatian
    'nl',  # Dutch
    'et',  # Estonian
    'fi',  # Finnish
    'fr',  # French
    'de',  # German
    'it',  # Italian
    'pl',  # Polish
    'es',  # Spanish
    'sv',  # Swedish
    'ru',  # Russian
]

# List of administrators (MusicBrainz usernames as strings)
ADMINS = []


# EXTERNAL SERVICES

# MusicBrainz
MUSICBRAINZ_HOSTNAME = None
MUSICBRAINZ_USERAGENT = "CritiqueBrainz"
MUSICBRAINZ_CLIENT_ID = ""
MUSICBRAINZ_CLIENT_SECRET = ""

# mbspotify
# https://github.com/metabrainz/mbspotify
MBSPOTIFY_BASE_URI = "http://mbspotify.musicbrainz.org/"
MBSPOTIFY_ACCESS_KEY = None
