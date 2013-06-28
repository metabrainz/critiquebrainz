from uuid import validate
from flask import request, abort
from functools import wraps

def uuid_or_400(key):
    def decorator(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            kwargs[key] = request.args.get(key)
            if not validate(request.args.get(key)):
                abort(400)
            return func(*args, **kwargs)
        return new_func
    return decorator
