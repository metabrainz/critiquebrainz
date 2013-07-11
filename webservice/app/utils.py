from werkzeug.routing import BaseConverter, ValidationError
from flask import request
from functools import wraps
from exceptions import *
from urllib import urlencode
from urlparse import urlparse
import re

def append_params_to_url(url, params):
    params = urlencode(params)
    if urlparse(url)[4]:
        return url + '&' + params
    else:
        return url + '?' + params

# useful fetching functions
def fetch_from_json_uuid(key):
    return fetch_from_json(key, validate_uuid)
    
def fetch_from_json_int(key):
    return fetch_from_json(key, converter=int)
    
def fetch_from_json_int_range(key, _min, _max):
    return fetch_from_json(key, lambda x: x in range(_min,_max+1), int)
    
def fetch_from_url_uuid(key):
    return fetch_from_url(key, validate_uuid)
    
def fetch_from_url_int(key):
    return fetch_from_url(key, converter=int)
    
def fetch_from_url_int_range(key, _min, _max):
    return fetch_from_url(key, lambda x: x in range(_min,_max+1), int)

def fetch_from_url_include(key, _model):
    return fetch_from_url(key, 
        lambda x: x in _model.VALID_INCLUDES,
        lambda x: x.split('+'))

# parameter fetching
def fetch_from_json(key, validator=None, converter=None):
    try:
        _dict = request.get_json()
    except:
        raise RequestBodyNotValidJSONError
    return fetch_from_dict(_dict, key, validator, converter)
    
def fetch_from_url(key, validator=None, converter=None):
    return fetch_from_dict(request.args, key, validator, converter)
    
def fetch_from_dict(_dict, key, validator=None, converter=None):
    """ Function used to fetch data from the `dict` dictionary object.
        The desired value can be validated using a function passed in
        `validator` parameter. It can also be coverted to desired format
        using a function passed in `converter` parameter. If the value is
        missing in the dictionary, MissingDataError exception is raised.
        If `validator` function returned False, or converter raised an 
        exception, the function raises NotValidData. """
    # fetching
    try:
        resp = _dict[key]
        if not resp: raise Exception
    except:
        raise MissingDataError(key) 
    # converting
    if converter is not None:
        try:
            resp = converter(resp)
        except:
            raise NotValidDataError(key)
    # validating
    if validator is not None:
        try:
            if not validator(resp): raise Exception
        except:
            raise NotValidDataError(key)
    return resp
        
    
# uuid-related utils
uuid_re = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    
def validate_uuid(value):
    try:
        return uuid_re.match(value)
    except TypeError:
        return False
        
class UUIDConverter(BaseConverter):
    
    def __init__(self, url_map, strict=True):
        super(UUIDConverter, self).__init__(url_map)
        self.strict = strict
    
    @classmethod
    def _register(cls, app):
        app.url_map.converters['uuid'] = cls
        
    def to_python(self, value):
        if self.strict and not validate_uuid(value):
            raise ValidationError()
        return value

    def to_url(self, value):
        return value

# rating-related utils
rate_threshold = [100, 10, 1]
ratio_threshold = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
rating = [[3, 2, 2, 1, 1, 0, 0, 0, -1, -1], [2, 2, 1, 1, 0, 0, 0, -1, -1, -1], 
          [1, 1, 0, 0, 0, -1, -1, -1, -1, -1]]    

def compute_rating(overall, positive):
    """ Compute a rating based on rates count and rates ratio. 
                    +-----------+-------------+-------------+
                    | 1-9 rates | 10-99 rates | >=100 rates |
        +-----------+-----------+-------------+-------------+
        | 3rd class |     -     |      -      |   x >= 90%  |
        +-----------+-----------+-------------+-------------+
        | 2nd class |     -     |   x >= 80%  |   x >= 70%  |
        +-----------+-----------+-------------+-------------+
        | 1st class |  x >= 80% |   x >= 60%  |   x >= 50%  |
        +-----------+-----------+-------------+-------------+
        | 0th class |  x >= 50% |   x >= 30%  |   x >= 20%  |
        +-----------+-----------+-------------+-------------+
        |-1th class |  x < 50%  |   x < 30%   |   x < 20%   |
        +-----------+-----------+-------------+-------------+
        x - positive rates/overall rates ratio
    """
    try:
        ratio = float(positive)/float(overall)
    except ZeroDivisionError:
        return 0

    for i in xrange(len(rate_threshold)):
        if overall >= rate_threshold[i]:
            break
                
    for j in xrange(len(ratio_threshold)):
        if ratio >= ratio_threshold[j]:
            break
                
    return rating[i][j]
