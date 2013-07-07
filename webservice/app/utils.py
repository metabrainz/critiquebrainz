import re
from werkzeug.routing import BaseConverter, ValidationError
from flask import request, abort
from functools import wraps

# decorators
def field(arg=None, json=None, converter=(lambda x: x), optional=False):
    """ Checks whether a request contains specified argument of UUID type,
        converts it using `converter` function, and passes it to the decorated
        function. """
    def decorator(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            try:
                if arg: kwargs[arg] = converter(request.values.get(arg))
                if json: kwargs[json] = converter(request.json.get(json))
            except:
                if not optional:
                    abort(400)
            return func(*args, **kwargs)
        return new_func
    return decorator

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
