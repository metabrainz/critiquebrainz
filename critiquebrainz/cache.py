import hashlib
import memcache

# Servers are reset during app creation process when configuration is available.
cache = memcache.Client(["127.0.0.1:11211"])

_namespace = "CB:"


def set_namespace(namespace):
    global _namespace
    _namespace = namespace


def generate_cache_key(id, type=None, source=None, params=None):
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
    key = key.replace(' ', '_')
    if len(key) > 250:  # 250 bytes is the maximum key length in memcached
        key = hashlib.sha1(key).hexdigest()
    return key
