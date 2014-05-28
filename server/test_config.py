DEBUG = True
TESTING = True
SQLALCHEMY_DATABASE_URI = "postgresql://cb_test:cb_test@localhost:5432/cb_test"

SECRET_KEY = ''

MUSICBRAINZ_CLIENT_ID = ''
MUSICBRAINZ_CLIENT_SECRET = ''

OAUTH_TOKEN_LENGTH = 40
OAUTH_GRANT_EXPIRE = 60
OAUTH_TOKEN_EXPIRE = 3600

# Mail server
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_FROM_ADDR = 'no-reply@' + MAIL_SERVER

# Logging
LOG_FILE = "server.log"
LOG_EMAIL_TOPIC = "CritiqueBrainz Server Failure"

# Administrator list (emails)
ADMINS = []
