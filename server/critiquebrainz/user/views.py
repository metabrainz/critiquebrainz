from flask import Blueprint, jsonify
from critiquebrainz.db import db, User
from critiquebrainz.exceptions import *
from critiquebrainz.oauth import oauth
from critiquebrainz.parser import Parser

bp = Blueprint('user', __name__)

@bp.route('/me', endpoint='me')
@oauth.require_auth()
def user_me_handler(user):
    try:
        inc = Parser.list('uri', 'inc', User.allowed_includes)
    except MissingDataError:
        inc = []
    return jsonify(user=user.to_dict(inc, confidental=True))

@bp.route('/me', endpoint='modify', methods=['POST'])
@oauth.require_auth('user')
def user_modify_handler(user):
    try:
        display_name = Parser.string('json', 'display_name', min=3, max=64)
        user.display_name = display_name
    except MissingDataError:
        pass     
    try:
        email = Parser.email('json', 'email')
        user.email = email
    except MissingDataError:
        pass
    db.session.commit()
    return jsonify(message='Request processed successfully')

@bp.route('/me', endpoint='delete', methods=['GET'])
@oauth.require_auth('user')
def user_delete_handler(user):
    db.session.delete(user)
    db.session.commit()
    return jsonify(message='Request processed successfully')

@bp.route('/<uuid:user_id>', endpoint='entity', methods=['GET'])
def user_entity_handler(user_id):
    user = User.query.get_or_404(str(user_id))
    try:
        include = Parser.list('uri', 'inc', User.allowed_includes)
    except MissingDataError:
        include = []
    return jsonify(user=user.to_dict(inc))
