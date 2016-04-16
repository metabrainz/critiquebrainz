# DEFAULT CONFIGURATION

SECRET_KEY = "secret"

# Database for testing
TEST_SQLALCHEMY_DATABASE_URI = "postgresql://cb_test:cb_test@localhost:5432/cb_test"

SQLALCHEMY_TRACK_MODIFICATIONS = False

# CritiqueBrainz OAuth configuration
OAUTH_TOKEN_LENGTH = 40
OAUTH_GRANT_EXPIRE = 60
OAUTH_TOKEN_EXPIRE = 3600

# Memcached
MEMCACHED_NAMESPACE = "CB"

# Mail server
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_FROM_ADDR = "no-reply@critiquebrainz.org"

# User-Agent string that is used to access MusicBrainz
MB_USERAGENT = "CritiqueBrainz"

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


# EXTERNAL SERVICES

# MusicBrainz
MUSICBRAINZ_HOSTNAME = None
MUSICBRAINZ_USERAGENT = "CritiqueBrainz Custom"
MUSICBRAINZ_CLIENT_ID = ""
MUSICBRAINZ_CLIENT_SECRET = ""

# mbspotify
MBSPOTIFY_BASE_URI = None
MBSPOTIFY_ACCESS_KEY = None
