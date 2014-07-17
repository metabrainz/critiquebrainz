# DEFAULT CONFIGURATION

# CritiqueBrainz server
CRITIQUEBRAINZ_BASE_URI = "http://127.0.0.1:5000/"

# Server with Spotify mappings
MBSPOTIFY_BASE_URI = "http://127.0.0.1:8080/"

MEMCACHED_SERVERS = ["127.0.0.1:11211"]
MEMCACHED_NAMESPACE = "CB_CLIENT"

# Mail server
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_FROM_ADDR = "no-reply@critiquebrainz.org"

# Logging
LOG_FILE = "client.log"
LOG_EMAIL_TOPIC = "CritiqueBrainz Client Failure"

# List of supported UI languages.
# Valid language codes can be obtained from Transifex.
SUPPORTED_LANGUAGES = [
    'en',  # English
    'de',  # German
    'es',  # Spanish
    'nl',  # Dutch
    'ru',  # Russian
    'el',  # Greek
    'hr',  # Croatian
    'eo',  # Esperanto
]
