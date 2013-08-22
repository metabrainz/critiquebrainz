from flask import Blueprint, jsonify, abort
from critiquebrainz.db import db, OAuthClient, OAuthToken
from critiquebrainz.exceptions import *
from critiquebrainz.oauth import oauth
from critiquebrainz.parser import Parser
from critiquebrainz.utils import generate_string

bp = Blueprint('client', __name__)

@bp.route('/<client_id>', endpoint='entity')
@oauth.require_auth('client')
def client_entity_handler(client_id, user):
    client = OAuthClient.query.get_or_404(client_id)
    if client.user_id != user.id:
        abort(403)
    inc = Parser.list('uri', 'inc', OAuthClient.allowed_includes, optional=True) or []
    return jsonify(client=client.to_dict(inc))

@bp.route('/<client_id>', methods=['POST'], endpoint='modify')
@oauth.require_auth('client')
def client_modify_handler(client_id, user):
    client = OAuthClient.query.get_or_404(client_id)
    if client.user_id != user.id:
        abort(403)
    name = Parser.string('json', 'name', min=3, max=64, optional=True)
    if name:
        client.name = name
    desc = Parser.string('json', 'desc', min=3, max=512, optional=True)
    if desc:
        client.desc = desc
    website = Parser.uri('json', 'website', optional=True)
    if website:
        client.website = website
    redirect_uri = Parser.uri('json', 'redirect_uri', optional=True)
    if redirect_uri:
        client.redirect_uri = redirect_uri
    scopes = Parser.list('json', 'scopes', optional=True)
    if scopes:
        client.scopes = ' '.join(scopes)
    db.session.commit()
    return jsonify(message='Request processed successfully')

@bp.route('/<client_id>', methods=['DELETE'], endpoint='delete')
@oauth.require_auth('client')
def client_delete_handler(client_id, user):
    client = OAuthClient.query.get_or_404(client_id)
    if client.user_id != user.id:
        abort(403)
    client.delete()
    return jsonify(message='Request processed successfully')

@bp.route('/', methods=['POST'], endpoint='create')
@oauth.require_auth('client')
def client_create_handler(user):
    name = Parser.string('json', 'name', min=3, max=64)
    desc = Parser.string('json', 'desc', min=3, max=512)
    website = Parser.uri('json', 'website')
    redirect_uri = Parser.uri('json', 'redirect_uri')
    scopes = Parser.list('json', 'scopes')
    client_id = generate_string(40)
    client_secret = generate_string(40)
    client = OAuthClient(client_id=client_id, client_secret=client_secret, user=user,
        name=name, desc=desc, website=website, redirect_uri=redirect_uri, scopes=' '.join(scopes))
    db.session.add(client)
    db.session.commit()
    return jsonify(message='Request processed successfully', client=dict(id=client_id, secret=client_secret))

@bp.route('/<client_id>/tokens', methods=['DELETE'], endpoint='delete_token')
@oauth.require_auth('client')
def token_delete_handler(client_id, user):
    token = OAuthToken.query.filter_by(client_id=client_id, user_id=user.id).delete()
    db.session.commit()
    return jsonify(message='Request processed successfully')

