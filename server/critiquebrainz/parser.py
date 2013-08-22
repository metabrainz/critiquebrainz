from flask import request
from critiquebrainz.utils import validate_uuid
from critiquebrainz.exceptions import MissingDataError, ParserError
from critiquebrainz.db import Publication
from urlparse import urlparse
import re

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
    def get_key(cls, src, key):
        _dict = cls.get_dict(src)
        _k = _dict.get(key)
        return _k

    @classmethod
    def string(cls, src, key, min=None, max=None, optional=False):
        _s = cls.get_key(src, key)
        if _s is None:
            if optional:
                return None
            else:
                raise MissingDataError(key)
        _s_len = len(_s)
        if max is not None and _s_len > max:
            raise ParserError(key, 'too long (max=%d)' % max)
        if min is not None and _s_len < min:
            raise ParserError(key, 'too short (min=%d)' % min)
        return _s

    @classmethod
    def int(cls, src, key, min=None, max=None, optional=False):
        _i = cls.get_key(src, key)
        if _i is None:
            if optional:
                return None
            else:
                raise MissingDataError(key)
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
        _u = cls.get_key(src, key)
        if _u is None:
            if optional:
                return None
            else:
                raise MissingDataError(key)
        if not validate_uuid(_u):
            raise ParserError(key, 'not valid UUID')
        return _u

    @classmethod
    def uri(cls, src, key, optional=False):
        _u = cls.get_key(src, key)
        if _u is None:
            if optional:
                return None
            else:
                raise MissingDataError(key)
        d = urlparse(_u)
        if d.scheme not in ['http', 'https'] or not d.netloc:
            raise ParserError(key, 'not valid URI')
        return _u

    @classmethod
    def email(cls, src, key, optional=False):
        _e = cls.get_key(src, key)
        if _e is None:
            if optional:
                return None
            else:
                raise MissingDataError(key)
        if not re.match("[^@]+@[^@]+\.[^@]+", _e):
            raise ParserError(key, 'not valid email')
        return _e

    @classmethod
    def list(cls, src, key, elements=None, optional=False):
        _l = cls.get_key(src, key)
        if _l is None:
            if optional:
                return None
            else:
                raise MissingDataError(key)
        _l = _l.split()
        if elements is not None:
            for e in _l:
                if e not in elements:
                    raise ParserError(key, 'contains illegal value `%s`' % e)
        return _l
