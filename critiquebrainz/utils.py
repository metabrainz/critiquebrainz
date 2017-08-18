import difflib
import urllib.parse
import string
import random
from flask import request
from flask_uuid import UUID_RE
from flask_babel import format_datetime, format_date

tags = {'+': ('<ins>', '</ins>'), '-': ('<del>', '</del>'), ' ': (' ', '')}


def build_url(base, additional_params=None):
    url = urllib.parse.urlparse(base)
    query_params = {}
    query_params.update(urllib.parse.parse_qsl(url.query, True))
    if additional_params is not None:
        query_params.update(additional_params)
        for key, val in additional_params.items():
            if val is None:
                query_params.pop(key)

    return urllib.parse.urlunparse(
        (url.scheme, url.netloc, url.path, url.params,
         urllib.parse.urlencode(query_params), url.fragment))


def validate_uuid(string):
    """Validates UUID. Returns True if valid, False otherwise."""
    return True if UUID_RE.match(string) else False


def generate_string(length):
    """Generates random string with a specified length."""
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits)
                   for _ in range(length))


def reformat_date(value, format=None):
    """Converts date into string formatted for current locale."""
    return format_date(value, format)


def reformat_datetime(value, format=None):
    """Converts datetime into string formatted for current locale."""
    return format_datetime(value.replace(tzinfo=None), format)


def track_length(value):
    """Converts track length specified in milliseconds into a pretty string."""
    seconds = int(value) / 1000
    minutes, seconds = divmod(seconds, 60)
    return '%i:%02i' % (minutes, seconds)


def parameterize(value, key):
    """
    Add a new parameter to the current url.

    Taken from: http://stackoverflow.com/a/2506477
    """
    url_parts = list(urllib.parse.urlparse(request.url))

    query = urllib.parse.parse_qs(url_parts[4])
    query[key] = value
    url_parts[4] = urllib.parse.urlencode(query, doseq=True)

    return urllib.parse.urlunparse(url_parts)


def side_by_side_diff(old, new):
    left, right = [], []

    # Deletions on the left, insertions on the right.
    def append(tag, text):
        if tag == '<ins>':
            right.append(text)
        elif tag == '<del>':
            left.append(text)
        else:
            left.append(text)
            right.append(text)

    # Generates a compact word diff
    prev_start, prev_end = None, ''
    prev_item = ''

    if old is None:
        old = ''
    if new is None:
        new = ''
    for item in difflib.ndiff(old.split(), new.split()):
        tag = tags.get(item[0])

        if not tag:
            continue

        if prev_start == tag[0]:
            prev_item += item[1:]
        else:
            append(prev_start, prev_item + prev_end)
            prev_start, prev_end = tag
            prev_item = prev_start + item[1:]

    append(prev_start, prev_item + prev_end)

    return " ".join(left), " ".join(right)
