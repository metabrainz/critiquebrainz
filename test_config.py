# Testing configuration

DEBUG = False
SECRET_KEY = "test"
WTF_CSRF_ENABLED = False
TESTING = True

# MusicBrainz Database
MB_DATABASE_URI = "postgresql://musicbrainz@musicbrainz_db:5432/musicbrainz_db"

# BookBrainz Database
BB_DATABASE_URI = "postgresql://bookbrainz:bookbrainz@db:5432/bookbrainz"