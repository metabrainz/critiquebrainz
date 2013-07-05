from flask import request, abort
from functools import wraps

def field(arg=None, json=None, converter=(lambda x: x), optional=False):
    '''
    Checks whether a request contains specified argument of UUID type.
    '''
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
