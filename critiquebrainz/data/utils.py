from critiquebrainz.data import db
from sqlalchemy import create_engine
from urlparse import urlsplit


def create_tables(app):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    db.metadata.create_all(engine)
    return engine


def explode_db_uri(uri):
    """Extracts database connection info from the URI.

    Returns hostname, database name, username and password.
    """
    uri = urlsplit(uri)
    return uri.hostname, uri.path[1:], uri.username, uri.password
