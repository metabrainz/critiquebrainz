from flask import Blueprint, jsonify, request, redirect, url_for
from critiquebrainz.db import db, User
from critiquebrainz.exceptions import *
from critiquebrainz.oauth import oauth
from critiquebrainz.parser import Parser

bp = Blueprint('user', __name__)

@bp.route('/me', endpoint='me')
@oauth.require_auth()
def user_me_handler(user):
    inc = Parser.list('uri', 'inc', User.allowed_includes, optional=True) or []
    return jsonify(user=user.to_dict(inc, confidential=True))

@bp.route('/me/reviews', endpoint='reviews')
@oauth.require_auth()
def user_reviews_handler(user):
    return redirect(url_for('review.list', user_id=user.id, **request.args))

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
    def fetch_params():
        display_name = Parser.string('json', 'display_name', optional=True)
        email = Parser.email('json', 'email', optional=True)
        show_gravatar = Parser.bool('json', 'show_gravatar', optional=True)
        return display_name, email, show_gravatar
    display_name, email, show_gravatar = fetch_params()
    user.update(display_name, email, show_gravatar)
    return jsonify(message='Request processed successfully')

@bp.route('/me', endpoint='delete', methods=['DELETE'])
@oauth.require_auth('user')
def user_delete_handler(user):
    user.delete()
    return jsonify(message='Request processed successfully')

@bp.route('/<uuid:user_id>', endpoint='entity', methods=['GET'])
def user_entity_handler(user_id):
    user = User.query.get_or_404(str(user_id))
    inc = Parser.list('uri', 'inc', User.allowed_includes, optional=True) or []
    return jsonify(user=user.to_dict(inc))

