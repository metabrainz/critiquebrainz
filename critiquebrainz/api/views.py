from critiquebrainz.exceptions import *
from publication.views import publication
from flask import jsonify

@publication.errorhandler(AbortError)
def api_abort_error_handler(error):
	return (jsonify(message=error.message), error.status_code)