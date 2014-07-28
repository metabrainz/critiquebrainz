from flask.ext.uuid import UUID_RE
from flask.ext.babel import format_datetime, format_date
import urllib
import urlparse
import string
import random


def build_url(base, additional_params=None):
    url = urlparse.urlparse(base)
    query_params = {}
    query_params.update(urlparse.parse_qsl(url.query, True))
    if additional_params is not None:
        query_params.update(additional_params)
        for k, v in additional_params.iteritems():
            if v is None:
                query_params.pop(k)

    return urlparse.urlunparse(
        (url.scheme, url.netloc, url.path, url.params, urllib.urlencode(query_params), url.fragment))


def validate_uuid(string):
    if not UUID_RE.match(string):
        return False
    else:
        return True


def generate_string(length):
    """Generates random string with a specified length."""
    return ''.join([random.choice(string.ascii_letters.decode('ascii') + string.digits.decode('ascii')) for x in xrange(length)])


def reformat_date(value, format=None):
    """Converts date into string formatted according to current locale."""
    return format_date(value, format)


def reformat_datetime(value, format=None):
    """Converts datetime into string formatted according to current locale."""
    return format_datetime(value.replace(tzinfo=None), format)


def track_length(value):
    """Converts track length from MusicBrainz into pretty string."""
    seconds = int(value) / 1000
    minutes, seconds = divmod(seconds, 60)
    return '%i:%02i' % (minutes, seconds)
