from uuid import validate
from flask import request, abort
from functools import wraps

def require_uuid(key):
    '''
    Checks whether a request contains specified argument of UUID type.
    '''
    def decorator(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            kwargs[key] = request.args.get(key)
            if not validate(request.args.get(key)):
                abort(400)
            return func(*args, **kwargs)
        return new_func
    return decorator
