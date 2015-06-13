from critiquebrainz.data import db
from sqlalchemy import create_engine
from urlparse import urlsplit
import unicodedata
import shutil
import errno
import sys
import os
import re


def create_tables(app):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], client_encoding='utf8')
    db.metadata.create_all(engine)
    return engine


def explode_db_uri(uri):
    """Extracts database connection info from the URI.

    Returns hostname, database name, username and password.
    """
    uri = urlsplit(uri)
    return uri.hostname, uri.path[1:], uri.username, uri.password


def slugify(string):
    """Converts unicode string to lowercase, removes alphanumerics and underscores, and converts spaces to hyphens.
    Also strips leading and trailing whitespace.
    """
    string = unicodedata.normalize('NFKD', string).encode('ascii', 'ignore').decode('ascii')
    string = re.sub('[^\w\s-]', '', string).strip().lower()
    return re.sub('[-\s]+', '-', string)


def create_path(path):
    """Creates a directory structure if it doesn't exist yet."""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            sys.exit("Failed to create directory structure %s. Error: %s" % (path, exception))


def get_columns(model):
    """Returns tuple of sorted columns for a specified model."""
    columns = model.__table__.columns._data.keys()
    columns.sort()
    return tuple(columns)


def remove_old_archives(location, pattern, is_dir=False, sort_key=None):
    """Removes all files or directories that match specified pattern except two last.

    Args:
        location: Location that needs to be cleaned up.
        pattern: Regular expression that will be used to filter entries in the specified location.
        is_dir: True if directories need to be removed, False if files.
        sort_key: See https://docs.python.org/2/howto/sorting.html?highlight=sort#key-functions.
    """
    entries = [os.path.join(location, e) for e in os.listdir(location)]
    pattern = re.compile(pattern)
    entries = filter(lambda x: pattern.search(x), entries)

    if is_dir:
        entries = filter(os.path.isdir, entries)
    else:
        entries = filter(os.path.isfile, entries)

    if sort_key is None:
        entries.sort()
    else:
        entries.sort(key=sort_key)

    # Leaving only two last entries
    for entry in entries[:(-2)]:
        print(' - %s' % entry)
        if is_dir:
            shutil.rmtree(entry)
        else:
            os.remove(entry)
