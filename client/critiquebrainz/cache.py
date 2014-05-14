import memcache
from critiquebrainz import app

cache = memcache.Client(app.config['MEMCACHED_SERVERS'], debug=0)


def generate_cache_key(id, type=None, source=None):
    key = app.config['MEMCACHED_NAMESPACE'] + ':'
    if source is not None:
        key += str(source) + ':'
    if type is not None:
        key += str(type) + ':'
    return key + str(id)