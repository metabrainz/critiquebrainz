"""
This module simplifies interaction with memcached. It uses python-memcached
package to interact with the server(s).

Module needs to be initialized before use. See init() function.

Package python-memcached is available at https://pypi.python.org/pypi/python-memcached/.
More information about memcached can be found at http://memcached.org/.
"""
import hashlib
import memcache

_mc = None
_namespace = "CB"


def init(servers, namespace="CB", debug=0):
    """Initializes memcached client.

    Args:
        server: List of strings with memcached server addresses (host:port).
        namespace: Optional namespace that will be prepended to all keys.
        debug: Whether to display error messages when a server can't be contacted.
    """
    global _mc, _namespace
    _mc = memcache.Client(servers, debug=debug)
    _namespace = namespace + ":"


def set(key, val, time=0, key_prefix=''):
    """Set a key to a given value.

    Returns:
        True if stored successfully, False otherwise.
    """
    if _mc is None: return
    not_stored = _mc.set_multi({key: val}, time, _namespace + key_prefix)
    return len(not_stored) == 0


def get(key, key_prefix=''):
    """Retrieve a key.

    Returns:
        Stored value or None if it's not found.
    """
    if _mc is None: return
    result = _mc.get_multi([key], _namespace + key_prefix)
    if key in result:
        return result[key]
    else:
        return None


def delete(key, key_prefix=''):
    """Delete a key.

    Returns:
          True if deleted successfully, False otherwise.
    """
    if _mc is None: return
    return _mc.delete_multi([key], key_prefix=_namespace + key_prefix) == 1


def set_multi(mapping, time=0, key_prefix=''):
    """Set multiple keys doing just one query.

    Args:
        mapping: A dict of key/value pairs to set.
    Returns:
        List of keys which failed to be stored (memcache out of memory, etc.).
    """
    if _mc is None: return
    return _mc.set_multi(mapping, time, _namespace + key_prefix)


def get_multi(keys, key_prefix=''):
    """Retrieve multiple keys doing just one query.

    Args:
        keys: Array of keys that need to be retrieved.
    Returns:
        A dictionary of key/value pairs that were available. If key_prefix was
        provided, the keys in the returned dictionary will not have it present.
    """
    if _mc is None: return
    return _mc.get_multi(keys, _namespace + key_prefix)


def prep_cache_key(key, attributes=None):
    """Creates a key with attached attributes.

    Args:
        key: Original key.
        attributes: List of attributes.
    Returns:
        New key that can be used with cache.
    """
    if _mc is None: return key

    if attributes is None:
        attributes = []

    if not isinstance(key, basestring):
        key = str(key)
    key = key.encode('ascii', errors='xmlcharrefreplace')

    for attr in attributes:
        if not isinstance(attr, basestring):
            attr = str(attr)
        key += '_' + attr.encode('ascii', errors='xmlcharrefreplace')
    key = key.replace(' ', '_')  # spaces are not allowed

    if _mc.server_max_key_length != 0 and \
        len(_namespace) + _mc.server_max_key_length:
        key = hashlib.sha1(key).hexdigest()

    _mc.check_key(_namespace + key)

    return key
