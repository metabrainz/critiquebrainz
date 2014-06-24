from flask import Blueprint, jsonify, abort
from critiquebrainz.db import db, OAuthClient, OAuthToken
from critiquebrainz.exceptions import *
from critiquebrainz.oauth import oauth
from critiquebrainz.parser import Parser

client_bp = Blueprint('client', __name__)

@client_bp.route('/<client_id>', endpoint='entity')
@oauth.require_auth('client')
def client_entity_handler(client_id, user):
    client = OAuthClient.query.get_or_404(client_id)
    if client.user_id != user.id:
        raise AccessDenied
    inc = Parser.list('uri', 'inc', OAuthClient.allowed_includes, optional=True) or []
    return jsonify(client=client.to_dict(inc))

@client_bp.route('/<client_id>', methods=['POST'], endpoint='modify')
@oauth.require_auth('client')
def client_modify_handler(client_id, user):
    def fetch_params():
        name = Parser.string('json', 'name', min=3, max=64, optional=True)
        desc = Parser.string('json', 'desc', min=3, max=512, optional=True)
        website = Parser.uri('json', 'website', optional=True)
        redirect_uri = Parser.uri('json', 'redirect_uri', optional=True)
        return name, desc, website, redirect_uri

    client = OAuthClient.query.get_or_404(client_id)
    if client.user_id != user.id:
        raise AccessDenied
    name, desc, website, redirect_uri = fetch_params()
    client.update(name, desc, website, redirect_uri)
    return jsonify(message='Request processed successfully')

@client_bp.route('/<client_id>', methods=['DELETE'], endpoint='delete')
@oauth.require_auth('client')
def client_delete_handler(client_id, user):
    client = OAuthClient.query.get_or_404(client_id)
    if client.user_id != user.id:
        raise AccessDenied
    client.delete()
    return jsonify(message='Request processed successfully')

@client_bp.route('/', methods=['POST'], endpoint='create')
@oauth.require_auth('client')
def client_create_handler(user):
    def fetch_params():
        name = Parser.string('json', 'name', min=3, max=64)
        desc = Parser.string('json', 'desc', min=3, max=512)
        website = Parser.uri('json', 'website')
        redirect_uri = Parser.uri('json', 'redirect_uri')
        return name, desc, website, redirect_uri

    name, desc, website, redirect_uri = fetch_params()
    client = OAuthClient.generate(user=user, name=name, desc=desc, website=website,
                                  redirect_uri=redirect_uri)
    return jsonify(message='Request processed successfully', client=client.to_dict())

@client_bp.route('/<client_id>/tokens', methods=['DELETE'], endpoint='tokens_purge')
@oauth.require_auth('client')
def tokens_purge_handler(client_id, user):
    OAuthToken.purge_tokens(client_id=client_id, user_id=user.id)
    return jsonify(message='Request processed successfully')
