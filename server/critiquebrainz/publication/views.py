from flask import Blueprint, jsonify, current_app, abort
from critiquebrainz.db import db, Publication
from critiquebrainz.exceptions import *
from critiquebrainz.oauth import oauth
from parsers import *

bp = Blueprint('publication', __name__)

@bp.route('/<uuid:publication_id>', endpoint='entity', methods=['GET'])
def publication_entity_handler(publication_id):
    publication = Publication.query.get_or_404(str(publication_id))
    include = parse_include_param() or []
    return jsonify(publication=publication.to_dict(include))

@bp.route('/<uuid:publication_id>', endpoint='delete', methods=['DELETE'])
@oauth.require_auth('publication')
def publication_delete_handler(publication_id, user):
    publication = Publication.query.get_or_404(str(publication_id))
    if publication.user_id != user.id:
        abort(403)
    db.session.delete(publication)
    db.session.commit()
    return jsonify(message='Request processed successfully')

@bp.route('/<uuid:publication_id>', endpoint='update', methods=['PUT'])
@oauth.require_auth('publication')
def publication_update_handler(publication_id, user):
    publication = Publication.query.get(str(publication_id))
    if publication is None:
        abort(404)
    if publication.user_id != user.id:
        abort(403)

    text = parse_text_param(min=25, max=2500)
    publication.text = text

    db.session.commit()

    return jsonify(message='Request processed successfully',
                   id=publication.id)
    
@bp.route('/', endpoint='list', methods=['GET'])
def publication_list_handler():
    release_group = parse_release_group_param()
    user_id = parse_user_id_param()
    limit = parse_limit_param(default=50, min=1, max=50)
    offset = parse_offset_param(default=0)
    rating = parse_rating_param(default=0)
    include = parse_include_param() or []

    if (release_group, user_id) == (None, None):
        raise InvalidRequest(desc='Neither `release_group` nor `user_id` was defined')

    publications, count = Publication.fetch_sorted_by_rating(release_group, 
        user_id, limit, offset, rating)

    return jsonify(limit=limit, offset=offset, count=count,
                   publications=[p.to_dict(include) for p in publications])

@bp.route('/', endpoint='post', methods=['POST'])
@oauth.require_auth('publication')
def publication_post_handler(user):
    release_group = parse_release_group_param(source='json')
    text = parse_text_param(min=25, max=2500)

    if Publication.query.filter_by(user=user, release_group=release_group).count():
        raise InvalidRequest(desc='You have already published a review for this album')

    publication = Publication.create(user=user, text=text, release_group=release_group)

    return jsonify(message='Request processed successfully',
                   id=publication.id)
