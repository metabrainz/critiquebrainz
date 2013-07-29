import urllib
import urlparse
import string
import random
from flask.ext.uuid import UUID_RE
import re

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

def format_datetime(value, format='%b %d, %Y'):
    from dateutil import parser
    date = parser.parse(value)
    native = date.replace(tzinfo=None)
    return native.strftime(format) 
