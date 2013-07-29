from flask import Blueprint, jsonify
from critiquebrainz.db import db, Publication
from critiquebrainz.exceptions import *
from critiquebrainz.oauth import oauth
from parsers import *

bp = Blueprint('user', __name__)

@bp.route('/me', endpoint='me')
@oauth.require_auth()
def user_me_handler(user):
    inc = parse_include_param() or []
    return jsonify(user=user.to_dict(inc))

@bp.errorhandler(AbortError)
def abort_error_handler(error):
    return (jsonify(message=error.message), error.status_code)
