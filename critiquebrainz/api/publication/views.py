from flask import Blueprint, jsonify
from flask.ext.login import login_required
from critiquebrainz.db import db, Publication
from critiquebrainz.exceptions import *
from critiquebrainz.oauth import oauth
from parsers import *

publication = Blueprint('publication', __name__, url_prefix='/publication')

@publication.route('/<uuid:publication_id>', endpoint='publication_by_id', methods=['GET'])
def publication_by_id_handler(publication_id):
	publication = Publication.query.get(publication_id)
	if publication is None:
		raise AbortError('Publication not found', 404)
	(include, ) = parse_include_param()
	return jsonify(publication=publication.to_dict(include))

@publication.route('/', endpoint='publication_list', methods=['GET'])
def publication_list_handler():
	release_group = parse_release_group_param()
	user_id = parse_user_id_param()
	limit = parse_limit_param(default=50, min=1, max=50)
	offset = parse_offset_param(default=0)
	rating = parse_rating_param(default=0)
	include = parse_include_param()

	if (release_group, user_id) == (None, None):
		raise AbortError('Neither `release_group` nor `user_id` was defined', 400)

	publications, count = Publication.fetch_sorted_by_rating(release_group, 
		user_id, limit, offset, rating)

	return jsonify(limit=limit, offset=offset, count=count,
                   publications=[p.to_dict(include) for p in publications])

@publication.route('/', endpoint='publication_post', methods=['POST'])
@oauth.require_oauth('publication')
def publication_post_handler(data):
	release_group = parse_release_group_param(source='json')
	text = parse_text_param()
	user = data.user

	try:
		publication = Publication.create(user=user, text=text, release_group=release_group)
	except:
		raise AbortError('Server could not complete the request', 500)

	return jsonify(message='Request processed successfully',
                       id=publication.id)

@publication.route('/<uuid:publication_id>', endpoint='publication_delete', methods=['DELETE'])
@oauth.require_oauth('publication')
def publication_delete_handler(publication_id, data):
	publication = Publication.query.get(publication_id)
	if publication is None:
		raise AbortError('Publication not found', 404)
	user = data.user
	if publication.user_id != user.id:
		raise AbortError('Access denied', 403)
	db.session.delete(publication)
	db.session.commit(db)
	return jsonify(message='Request processed successfully')

@publication.route('/<uuid:publication_id>', endpoint='publication_edit', methods=['PUT'])
@oauth.require_oauth('publication')
def publication_edit_handler(publication_id, data):
	text = parse_text_param()
	user = data.user

	publication = Publication.query.get(publication_id)
	if publication is None:
		raise AbortError('Publication not found', 404)
	if publication.user_id != user.id:
		raise AbortError('Access denied', 403)
	publication.text = text
	db.session.commit(db)
	return jsonify(message='Request processed successfully',
                    	id=publication.id)
	