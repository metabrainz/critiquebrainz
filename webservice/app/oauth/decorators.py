from app.utils.uuid import validate
from flask import request, abort, jsonify
from functools import wraps

def require_user(func):
    '''
    Authorizes access to an API call.
    * temporary implementation *
    * requires additional field `user_id` in request *
    '''
    @wraps(func)
    def new_func(*args, **kwargs):
        kwargs['user_id'] = request.json.get('user_id')
        return func(*args, **kwargs)
    return new_func
