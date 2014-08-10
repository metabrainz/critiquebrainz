# DEFAULT CONFIGURATION

# Primary database
SQLALCHEMY_DATABASE_URI = "postgresql://cb:cb@localhost:5432/cb"

# Database for testing
TEST_SQLALCHEMY_DATABASE_URI = "postgresql://cb_test:cb_test@localhost:5432/cb_test"

SSL_AVAILABLE = True

# CritiqueBrainz OAuth configuration
OAUTH_TOKEN_LENGTH = 40
OAUTH_GRANT_EXPIRE = 60
OAUTH_TOKEN_EXPIRE = 3600

# Server with Spotify mappings
MBSPOTIFY_BASE_URI = "http://127.0.0.1:8080/"

# Memcached
MEMCACHED_SERVERS = ["127.0.0.1:11211"]
MEMCACHED_NAMESPACE = "CB"

# Mail server
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_FROM_ADDR = "no-reply@critiquebrainz.org"

# Logging
LOG_FILE = "server.log"
LOG_EMAIL_TOPIC = "CritiqueBrainz Failure"

# List of supported UI languages.
# Valid language codes can be obtained from Transifex.
SUPPORTED_LANGUAGES = [
    'en',  # English
    'es',  # Spanish
    'ru',  # Russian
    'el',  # Greek
    'de',  # German
    'fr',  # French
    'fi',  # Finnish
    'eo',  # Esperanto
    'nl',  # Dutch
    'hr',  # Croatian
]
