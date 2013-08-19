from flask import Blueprint, jsonify, abort
from critiquebrainz.db import db, OAuthClient
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
    try:
        inc = Parser.list('uri', 'inc', OAuthClient.allowed_includes)
    except MissingDataError:
        inc = []
    return jsonify(client=client.to_dict(inc))

@bp.route('/<client_id>', methods=['POST'], endpoint='modify')
@oauth.require_auth('client')
def client_modify_handler(client_id, user):
    client = OAuthClient.query.get_or_404(client_id)
    if client.user_id != user.id:
        abort(403)
    try:
        name = Parser.string('json', 'name', min=3, max=64)
        client.name = name
    except MissingDataError:
        pass
    try:
        desc = Parser.string('json', 'desc', min=3, max=512)
        client.desc = desc
    except MissingDataError:
        pass
    try:
        website = Parser.uri('json', 'website')
        client.website = website
    except MissingDataError:
        pass
    try:
        redirect_uri = Parser.uri('json', 'redirect_uri')
        client.redirect_uri = redirect_uri
    except MissingDataError:
        pass
    try:
        scopes = Parser.list('json', 'scopes')
        client.scopes = ' '.join(scopes)
    except MissingDataError:
        pass
    db.session.commit()
    return jsonify(message='Request processed successfully')

@bp.route('/<client_id>', methods=['DELETE'], endpoint='delete')
@oauth.require_auth('client')
def client_delete_handler(client_id, user):
    client = OAuthClient.query.get_or_404(client_id)
    if client.user_id != user.id:
        abort(403)
    db.session.delete(client)
    db.session.commit()
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