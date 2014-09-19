"""
This module simplifies interaction with memcached. It uses python-memcached package to create client.

Connection info is loaded from custom configuration file (config.py) or default configuration file
(default_config.py) if custom file doesn't exist.

Package python-memcached is available at https://pypi.python.org/pypi/python-memcached/.
More information about memcached can be found at http://memcached.org/.
"""
import hashlib
import memcache

# Trying to load configuration
try:
    import config
    cache = memcache.Client(config.MEMCACHED_SERVERS)
    _namespace = config.MEMCACHED_NAMESPACE
except (ImportError, AttributeError):
    import default_config
    cache = memcache.Client(default_config.MEMCACHED_SERVERS)
    _namespace = default_config.MEMCACHED_NAMESPACE


def set_namespace(namespace):
    """Sets namespace for cache keys that will be generated.

    Default namespace is defined in default config file. You can set
    your own default value by modifying custom config file.
    """
    global _namespace
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
