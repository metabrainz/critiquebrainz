from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from urlparse import urlsplit

db = SQLAlchemy()


def create_tables(app):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    db.metadata.create_all(engine)
    return engine


def explode_db_url(url):
    """Extracts database connection info from the URL.

    Returns hostname, database name, username and password.
    """
    url = urlsplit(url)
    return url.hostname, url.path[1:], url.username, url.password
