DEBUG = False
TESTING = True
SECRET_KEY = "test"
WTF_CSRF_ENABLED = False

SQLALCHEMY_DATABASE_URI = "postgresql://critiquebrainz:critiquebrainz@db_test:5432/critiquebrainz"

# Logging
LOG_FILE = None
LOG_EMAIL = None
LOG_SENTRY = None

# MusicBrainz
MUSICBRAINZ_HOSTNAME = "musicbrainz.org"
MUSICBRAINZ_USERAGENT = "CritiqueBrainz Test Runner"
MUSICBRAINZ_CLIENT_ID = ""
MUSICBRAINZ_CLIENT_SECRET = ""

# MBSpotify
MBSPOTIFY_BASE_URI = "https://mbspotify.musicbrainz.org/"
MBSPOTIFY_ACCESS_KEY = ""

# Mail server
MAIL_SERVER = None
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# OAuth
OAUTH_TOKEN_LENGTH = 40
OAUTH_GRANT_EXPIRE = 60
OAUTH_TOKEN_EXPIRE = 3600

# Redis
REDIS_HOST = 'critiquebrainz_redis'
REDIS_PORT = 6379
REDIS_NAMESPACE = 'CB'
