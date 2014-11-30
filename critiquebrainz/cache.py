"""
This module simplifies interaction with memcached. It uses python-memcached
package to interact with the server(s).

Module needs to be initialized before use. See init() function.

Package python-memcached is available at https://pypi.python.org/pypi/python-memcached/.
More information about memcached can be found at http://memcached.org/.
"""
import hashlib
import memcache

mc = None
_namespace = ""


def init(servers, namespace="", debug=0):
    """Initializes memcached client.

    Args:
        server: List of strings with memcached server addresses (host:port).
        namespace: Optional namespace that will be prepended to all keys.
        debug: Whether to display error messages when a server can't be contacted.
    """
    global mc, _namespace
    mc = memcache.Client(servers, debug=debug)
    _namespace = namespace


def generate_cache_key(id, type=None, source=None, params=None):
    """Generates cache key that can be used to fetch items from cache and save them.

    You can provide additional arguments that describe item that you are going to
    put in cache in a unique way.
    """
    if params is None:
        params = []
    key = _namespace + ':'

    if source is not None:
        key += str(source) + ':'
    if type is not None:
        key += str(type) + ':'
    key += str(id)
    for param in params:
        if not isinstance(param, basestring):
            param = str(param)
        key += '_' + param.encode('ascii', 'ignore')
    key = key.replace(' ', '_')  # spaces are not allowed

    if len(key) > 250:  # 250 bytes is the maximum key length in memcached
        key = hashlib.sha1(key).hexdigest()

    return key
