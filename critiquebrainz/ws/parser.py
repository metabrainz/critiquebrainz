import urllib.parse
import re
from flask import request
from critiquebrainz.utils import validate_uuid
from critiquebrainz.ws.exceptions import MissingDataError, ParserError


class Parser(object):

    @classmethod
    def get_dict(cls, src):
        if src == 'uri':
            return request.args
        elif src == 'form':
            return request.form
        elif src == 'json':
            return request.json

    @classmethod
    def get_key(cls, src, key, optional):
        _dict = cls.get_dict(src)
        if key not in _dict and not optional:
            raise MissingDataError(key)
        return _dict.get(key)

    @classmethod
    def bool(cls, src, key, optional=False):
        _b = cls.get_key(src, key, optional)
        if _b is None:
            return None
        if isinstance(_b, bool) is False:
            raise ParserError(key, 'is not bool')
        return _b

    @classmethod
    def string(cls, src, key, min=None, max=None, valid_values=None, optional=False):
        _s = cls.get_key(src, key, optional)
        if _s is None:
            return None
        _s_len = len(_s)
        if max is not None and _s_len > max:
            raise ParserError(key, 'too long (max=%d)' % max)
        if min is not None and _s_len < min:
            raise ParserError(key, 'too short (min=%d)' % min)
        if valid_values is not None and _s not in valid_values:
            raise ParserError(key, 'is not valid')
        return _s

    @classmethod
    def int(cls, src, key, min=None, max=None, optional=False):
        _i = cls.get_key(src, key, optional)
        if _i is None:
            return None
        if _i.isdigit() is False:
            raise ParserError(key, 'NaN')
        else:
            _i = int(_i)
        if max is not None and _i > max:
            raise ParserError(key, 'too large (max=%d)' % max)
        if min is not None and _i < min:
            raise ParserError(key, 'too small (min=%d)' % min)
        return _i

    @classmethod
    def uuid(cls, src, key, optional=False):
        _u = cls.get_key(src, key, optional)
        if _u is None:
            return None
        if not validate_uuid(_u):
            raise ParserError(key, 'not valid UUID')
        return _u

    @classmethod
    def uri(cls, src, key, optional=False):
        _u = cls.get_key(src, key, optional)
        if _u is None:
            return None
        d = urllib.parse.urlparse(_u)
        if d.scheme not in ['http', 'https'] or not d.netloc:
            raise ParserError(key, 'not valid URI')
        return _u

    @classmethod
    def email(cls, src, key, optional=False):
        _e = cls.get_key(src, key, optional)
        if not _e:
            return None
        if not re.match("[^@]+@[^@]+\.[^@]+", _e):
            raise ParserError(key, 'not valid email')
        return _e

    @classmethod
    def list(cls, src, key, elements=None, optional=False):
        _l = cls.get_key(src, key, optional)
        if _l is None:
            return None
        _l = _l.split()
        if elements is not None:
            for e in _l:
                if e not in elements:
                    raise ParserError(key, 'contains illegal value `%s`' % e)
        return _l
