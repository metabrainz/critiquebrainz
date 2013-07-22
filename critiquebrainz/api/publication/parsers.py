from flask import request
from critiquebrainz.utils import validate_uuid
from critiquebrainz.exceptions import *

# json/query
def parse_release_group_param(source='query'):
	if source == 'query':
		release_group = request.args.get('release_group', None)
	elif source == 'json':
		release_group = request.json.get('release_group', None)
	if release_group is not None and not validate_uuid(release_group):
		raise AbortError('Parameter `release_group` not valid', 400)
	return release_group

# json
def parse_text_param():
	text = request.json.get('text', None)
	if text is None:
		raise AbortError('Parameter `text` is missing', 400)
	return text

# query
def parse_user_id_param():
	user_id = request.args.get('user_id', None)
	if user_id is not None and not validate_uuid(user_id):
		raise AbortError('Parameter `user_id` not valid', 400)
	return user_id
	
def parse_include_param():
	include = request.args.get('inc', None)
	if include is not None and include not in Publication.allowed_includes:
		raise AbortError('Parameter `include` not valid', 400)
	return include

def parse_limit_param(default, min, max):
	limit = request.args.get('limit')
	if limit is None:
		return default

	if limit.isdigit() is False:
		raise AbortError('Parameter `limit` is NaN', 400)

	limit = int(limit)
	if limit not in range(min, max+1):
		raise AbortError('Parameter `limit` should be between %d and %d' \
			'(default %d)' % (min, max, default), 400)
	return limit

def parse_offset_param(default):
	offset = request.args.get('offset')
	if offset is None:
		return default

	if offset.isdigit() is False:
		raise AbortError('Parameter `offset` is NaN', 400)
	offset = int(offset)
	return offset

def parse_rating_param(default):
	rating = request.args.get('rating')
	if rating is None:
		return default

	if rating.isdigit() is False:
		raise AbortError('Parameter `rating` is NaN', 400)

	rating = int(rating)
	if rating not in [-1, 0, 1, 2, 3]:
		raise AbortError('Parameter `rating` should be between -1 and 3 '\
			'(default %d)' % default, 400)

	return rating
