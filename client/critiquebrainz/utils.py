from flask.ext.uuid import UUID_RE
from flask.ext.babel import format_datetime, format_date
from dateutil import parser
import urllib
import urlparse
import string
import random


def generate_string(length):
    return ''.join([random.choice(string.ascii_letters.decode('ascii') + string.digits.decode('ascii')) for x in xrange(length)])


def build_url(base, additional_params=None):
    url = urlparse.urlparse(base)
    query_params = {}
    query_params.update(urlparse.parse_qsl(url.query, True))
    if additional_params is not None:
        query_params.update(additional_params)
        for k, v in additional_params.iteritems():
            if v is None:
                query_params.pop(k)

    return urlparse.urlunparse((url.scheme,
                                url.netloc,
                                url.path,
                                url.params,
                                urllib.urlencode(query_params),
                                url.fragment))


def validate_uuid(string):
    if not UUID_RE.match(string):
        return False
    else:
        return True


def reformat_date(value, format=None):
    return format_date(parser.parse(value), format)


def reformat_datetime(value, format=None):
    return format_datetime(parser.parse(value).replace(tzinfo=None), format)


def track_length(value):
    seconds = int(value) / 1000
    minutes, seconds = divmod(seconds, 60)
    return '%i:%02i' % (minutes, seconds)
