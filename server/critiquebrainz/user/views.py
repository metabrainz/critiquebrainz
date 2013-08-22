from flask import Blueprint, jsonify
from critiquebrainz.db import db, User
from critiquebrainz.exceptions import *
from critiquebrainz.oauth import oauth
from critiquebrainz.parser import Parser

bp = Blueprint('user', __name__)

@bp.route('/me', endpoint='me')
@oauth.require_auth()
def user_me_handler(user):
    inc = Parser.list('uri', 'inc', User.allowed_includes, optional=True) or []
    return jsonify(user=user.to_dict(inc, confidental=True))

@bp.route('/me/publications', endpoint='publications')
@oauth.require_auth()
def user_publications_handler(user):
    return jsonify(publications=[p.to_dict() for p in user.publications])

@bp.route('/me/clients', endpoint='clients')
@oauth.require_auth()
def user_clients_handler(user):
    return jsonify(clients=[c.to_dict() for c in user.clients])
    
@bp.route('/me/tokens', endpoint='tokens')
@oauth.require_auth()
def user_tokens_handler(user):
    return jsonify(tokens=[t.to_dict() for t in user.tokens])
    
@bp.route('/me', endpoint='modify', methods=['POST'])
@oauth.require_auth('user')
def user_modify_handler(user):
    display_name = Parser.string('json', 'display_name', optional=True)
    if display_name:
        user.display_name = display_name
    email = Parser.email('json', 'email', optional=True)
    if email:
        user.email = email
    db.session.commit()
    return jsonify(message='Request processed successfully')

@bp.route('/me', endpoint='delete', methods=['DELETE'])
@oauth.require_auth('user')
def user_delete_handler(user):
    user.delete()
    return jsonify(message='Request processed successfully')

@bp.route('/<uuid:user_id>', endpoint='entity', methods=['GET'])
def user_entity_handler(user_id):
    user = User.query.get_or_404(str(user_id))
    include = Parser.list('uri', 'inc', User.allowed_includes) or []
    return jsonify(user=user.to_dict(inc))

