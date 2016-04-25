"""
This module serves as an interface to memcached instance.

Module needs to be initialized before use. See init() function.

It basically serves as a wrapper for pymemcache package with additional
functionality and tweaks specific to serve our needs.

There's also support for namespacing, which simplifies management of different
versions of data saved in the cache. You can invalidate whole namespace using
invalidate_namespace() function. See its description for more info.

More information about memcached can be found at https://memcached.org/.
"""
from pymemcache.client.hash import HashClient
import hashlib
import msgpack
import datetime

_mc = None  # type: HashClient
_glob_namespace = b"CB"

# FIXME(roman): There's potentially a big problem with storing namespace versions in
# the same place (memcached). These can get removed if cache becomes too big. It
# might be a better idea to offload them into a separate system (like redis).

SHA1_LENGTH = 40
MAX_KEY_LENGTH = 250
CONTENT_ENCODING = "utf-8"


def init(servers, namespace="CB"):
    """Initializes memcached client. Needs to be called before use.

    Args:
        servers: List of strings with memcached server addresses (host:port).
        namespace: Optional global namespace that will be prepended to all keys.
    """
    global _mc, _glob_namespace
    _mc = HashClient(
        servers=servers,
        serializer=_serializer,
        deserializer=_deserializer,
    )
    _glob_namespace = namespace + ":"
    _glob_namespace = _glob_namespace.encode("ascii")
    if len(_glob_namespace) + SHA1_LENGTH > MAX_KEY_LENGTH:
        raise ValueError("Namespace is too long.")


def set(key, val, time=0, namespace=None):
    """Set a key to a given value.

    Args:
        key: Key of the item.
        val: Item's value.
        time: The time after which this value should expire, either as a delta
            number of seconds, or an absolute unix time-since-the-epoch value.
            If set to 0, value will be stored "forever".
        namespace: Optional namespace in which key needs to be defined.

    Returns:
        True if stored successfully.
    """
    if _mc is None: return
    return set_many({key: val}, time, namespace)


def get(key, namespace=None):
    """Retrieve an item.

    Args:
        key: Key of the item that needs to be retrieved.
        namespace: Optional namespace in which key was defined.

    Returns:
        Stored value or None if it's not found.
    """
    if _mc is None: return
    result = get_many([key], namespace)
    return result.get(key)


def delete(key, namespace=None):
    """Delete an item.

    Args:
        key: Key of the item that needs to be deleted.
        namespace: Optional namespace in which key was defined.

    Returns:
          True if deleted successfully.
    """
    if _mc is None: return
    return delete_many([key], namespace) == 1


def set_many(mapping, time=0, namespace=None):
    """Set multiple keys doing just one query.

    Args:
        mapping: A dict of key/value pairs to set.
        time: Time to store the keys (in milliseconds).
        namespace: Namespace for the keys.

    Returns:
        True on success.
    """
    if _mc is None: return
    return _mc.set_many(_prep_dict(mapping, namespace), time)


def get_many(keys, namespace=None):
    """Retrieve multiple keys doing just one query.

    Args:
        keys: Array of keys that need to be retrieved.
        namespace: Namespace for the keys.

    Returns:
        A dictionary of key/value pairs that were available.
    """
    if _mc is None: return {}
    res = _mc.get_many(_prep_list(keys, namespace))
    for k in keys:
        if namespace:
            namespace_and_version = _append_namespace_version(namespace)
        else:
            namespace_and_version = None
        prep = _prep_key(k, namespace_and_version)
        if prep in res:
            res[k] = _decode_value(res.pop(prep))
    return res


def delete_many(keys, namespace=None):
    if _mc is None: return
    return _mc.delete_many(_prep_list(keys, namespace))


def gen_key(key, *attributes):
    """Helper function that generates a key with attached attributes.

    Args:
        key: Original key.
        attributes: Attributes that will be appended a key.

    Returns:
        Key that can be used with cache.
    """
    if not isinstance(key, str):
        key = str(key)
    key = key.encode('ascii', errors='xmlcharrefreplace')

    for attr in attributes:
        if not isinstance(attr, str):
            attr = str(attr)
        key += b'_' + attr.encode('ascii', errors='xmlcharrefreplace')

    key = key.replace(b' ', b'_')  # spaces are not allowed

    return key


def invalidate_namespace(namespace):
    """Invalidates specified namespace.

    Invalidation is done by incrementing version of the namespace

    Args:
        namespace: Namespace that needs to be invalidated.

    Returns:
        True on success.
    """
    if _mc is None: return
    version_key = _glob_namespace + namespace.encode("ascii")
    current = _mc.get(version_key)
    if current is None:  # namespace isn't initialized
        return _mc.set(version_key, 1)  # initializing the namespace
    else:
        return _mc.set(version_key, current + 1)


def flush_all():
    if _mc is None: return
    _mc.flush_all()


def _append_namespace_version(namespace):
    if _mc is None: return
    version_key = _glob_namespace + namespace.encode("ascii")
    version = _mc.get(version_key)
    if version is None:  # namespace isn't initialized
        version = 1
        _mc.set(version_key, version)  # initializing the namespace
    return "%s:%s" % (namespace, version)


def _prep_key(key, namespace_and_version=None):
    """Prepares a key for use with memcached."""
    if _mc is None: return
    if namespace_and_version:
        key = "%s:%s" % (namespace_and_version, key)
    if not isinstance(key, bytes):
        key = key.encode('ascii', errors='xmlcharrefreplace')
    key = hashlib.sha1(key).hexdigest().encode('ascii')
    key = _glob_namespace + key
    return key


def _prep_list(l, namespace=None):
    """Wrapper for _prep_key function that works with lists."""
    if namespace:
        namespace_and_version = _append_namespace_version(namespace)
    else:
        namespace_and_version = None
    return [_prep_key(k, namespace_and_version) for k in l]


def _prep_dict(dictionary, namespace=None):
    """Wrapper for _prep_key function that works with dictionaries."""
    if namespace:
        namespace_and_version = _append_namespace_version(namespace)
    else:
        namespace_and_version = None
    return {_prep_key(key, namespace_and_version): value
            for key, value in dictionary.items()}


def _encode_value(value):
    if isinstance(value, str):
        value = value.encode(CONTENT_ENCODING)
    return value


def _decode_value(value):
    if isinstance(value, bytes):
        value = value.decode(CONTENT_ENCODING)
    return value


######################
# CUSTOM SERIALIZATION
######################

TYPE_DATETIME_CODE = 1


def _serializer(key, value):
    if type(value) == str:
        return _encode_value(value), 1
    return msgpack.packb(value, use_bin_type=True, default=_default), 2


def _deserializer(key, value, flags):
    if flags == 1:
        return _decode_value(value)
    if flags == 2:
        return msgpack.unpackb(value, encoding='utf-8', ext_hook=_ext_hook)
    raise ValueError("Unknown serialization format.")


def _default(obj):
    if isinstance(obj, datetime.datetime):
        return msgpack.ExtType(TYPE_DATETIME_CODE, obj.strftime("%Y%m%dT%H:%M:%S.%f").encode(CONTENT_ENCODING))
    raise TypeError("Unknown type: %r" % (obj,))


def _ext_hook(code, data):
    if code == TYPE_DATETIME_CODE:
        return datetime.datetime.strptime(_decode_value(data), "%Y%m%dT%H:%M:%S.%f")
    return msgpack.ExtType(code, data)
