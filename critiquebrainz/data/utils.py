import errno
import os
import re
import shutil
import sys
import unicodedata
import urllib.parse
from functools import wraps

from critiquebrainz import db
from critiquebrainz import frontend

ADMIN_SQL_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'admin', 'sql')


def create_all():
    db.run_sql_script_without_transaction(os.path.join(ADMIN_SQL_DIR, 'create_extensions.sql'))
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_types.sql'))
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_tables.sql'))
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_primary_keys.sql'))
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_foreign_keys.sql'))
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'create_indexes.sql'))


def drop_tables():
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'drop_tables.sql'))


def drop_types():
    db.run_sql_script(os.path.join(ADMIN_SQL_DIR, 'drop_types.sql'))


def explode_db_uri(uri):
    """Extracts database connection info from the URI.

    Returns hostname, database name, username and password.
    """
    uri = urllib.parse.urlsplit(uri)
    return uri.hostname, uri.port, uri.path[1:], uri.username, uri.password


def slugify(string):
    """Converts unicode string to lowercase, removes alphanumerics and underscores, and converts spaces to hyphens.
    Also strips leading and trailing whitespace.
    """
    string = unicodedata.normalize('NFKD', string).encode('ascii', 'ignore').decode('ascii')
    string = re.sub(r'[^\w\s-]', '', string).strip().lower()
    return re.sub(r'[-\s]+', '-', string)


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
    entries = filter(pattern.search, entries)

    if is_dir:
        entries = filter(os.path.isdir, entries)
    else:
        entries = filter(os.path.isfile, entries)

    entries = list(entries)

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


def with_request_context(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        with frontend.create_app().test_request_context():
            return f(*args, **kwargs)

    return decorated


def with_test_request_context(f):
    """Decorator for providing request context for application during tests."""

    @wraps(f)
    def decorated(*args, **kwargs):
        with frontend.create_app(config_path=os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    '..', '..', 'test_config.py')).test_request_context():
            return f(*args, **kwargs)

    return decorated
