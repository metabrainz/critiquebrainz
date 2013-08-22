from flask import Blueprint, jsonify, current_app, abort
from critiquebrainz.db import db, Publication
from critiquebrainz.exceptions import *
from critiquebrainz.oauth import oauth
from critiquebrainz.parser import Parser

bp = Blueprint('publication', __name__)

@bp.route('/<uuid:publication_id>', endpoint='entity', methods=['GET'])
def publication_entity_handler(publication_id):
    publication = Publication.query.get_or_404(str(publication_id))
    include = Parser.list('uri', 'inc', Publication.allowed_includes, optional=True) or []
    return jsonify(publication=publication.to_dict(include))

@bp.route('/<uuid:publication_id>', endpoint='delete', methods=['DELETE'])
@oauth.require_auth('publication')
def publication_delete_handler(publication_id, user):
    publication = Publication.query.get_or_404(str(publication_id))
    if publication.user_id != user.id:
        abort(403)
    publication.delete()
    return jsonify(message='Request processed successfully')

@bp.route('/<uuid:publication_id>', endpoint='modify', methods=['POST'])
@oauth.require_auth('publication')
def publication_modify_handler(publication_id, user):
    publication = Publication.query.get_or_404(str(publication_id))
    if publication.user_id != user.id:
        abort(403)
    text = Parser.string('json', 'text', min=25, max=2500)    
    publication.text = text
    db.session.commit()
    return jsonify(message='Request processed successfully',
                   publication=dict(id=publication.id))
    
@bp.route('/', endpoint='list', methods=['GET'])
def publication_list_handler():
    release_group = Parser.uuid('uri', 'release_group', optional=True)
    user_id = Parser.uuid('uri', 'user_id', optional=True)
    limit = Parser.int('uri', 'limit', min=1, max=50, optional=True) or 50
    offset = Parser.int('uri', 'offset', optional=True) or 0
    rating = Parser.int('uri', 'rating', min=-1, max=3, optional=True) or 0
    include = Parser.list('uri', 'inc', Publication.allowed_includes, optional=True) or []

    if (release_group, user_id) == (None, None):
        raise InvalidRequest(desc='Neither `release_group` nor `user_id` was defined')

    publications, count = Publication.fetch_sorted_by_rating(release_group, 
        user_id, limit, offset, rating)

    return jsonify(limit=limit, offset=offset, count=count,
                   publications=[p.to_dict(include) for p in publications])

@bp.route('/', endpoint='create', methods=['POST'])
@oauth.require_auth('publication')
def publication_post_handler(user):
    release_group = Parser.uuid('json', 'release_group')
    text = Parser.string('json', 'text', min=25, max=2500)

    if Publication.query.filter_by(user=user, release_group=release_group).count():
        raise InvalidRequest(desc='You have already published a review for this album')

    publication = Publication.create(user=user, text=text, release_group=release_group)

    return jsonify(message='Request processed successfully',
                   id=publication.id)

