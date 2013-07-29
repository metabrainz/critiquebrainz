from flask import request
from critiquebrainz.utils import validate_uuid
from critiquebrainz.exceptions import *
from critiquebrainz.db import User

def parse_include_param():
	include = request.args.get('inc')
	if include:
		includes = include.split()
		for include in includes:
			if include not in User.allowed_includes:
				raise AbortError('Parameter `include` not valid', 400)
		return includes
	else:
		return None