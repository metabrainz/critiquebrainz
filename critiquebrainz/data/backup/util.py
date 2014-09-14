from flask.json import JSONEncoder
from datetime import datetime
import unicodedata
import shutil
import errno
import os
import re


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
            raise


def remove_old_archives(location, pattern, is_dir=False, sort_key=None):
    """Removes all files or directories that match specified pattern except two last.

    :param location: Location that needs to be cleaned up.
    :param pattern: Regular expression that will be used to filter entries in the specified location.
    :param is_dir: True if directories need to be removed, False if files.
    :param sort_key: See https://docs.python.org/2/howto/sorting.html?highlight=sort#key-functions.
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


class DumpJSONEncoder(JSONEncoder):
    """Custom JSON encoder for database dumps."""
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
