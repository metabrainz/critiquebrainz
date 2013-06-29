from uuid import validate
from flask import request, abort,jsonify
from functools import wraps

def require_uuid(arg=None, json=None):
    '''
    Checks whether a request contains specified argument of UUID type.
    '''
    def decorator(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            if arg:
                kwargs[arg] = request.values.get(arg)
                if not validate(kwargs[arg]):
                    abort(400)
            if json:
                kwargs[json] = request.json.get(json)
                if not validate(kwargs[json]):
                    abort(400)
            return func(*args, **kwargs)
        return new_func
    return decorator
