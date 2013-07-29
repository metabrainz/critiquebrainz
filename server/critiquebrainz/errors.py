from critiquebrainz.exceptions import *
from critiquebrainz import app

@app.errorhandler(AbortError)
def abort_error_handler(error):
    return (jsonify(error=error.message), error.status_code)

@app.errorhandler(OAuthError)
def oauth_error_handler(error):
    return abort_error_handler(AbortError('Not authorized', 401))

@app.errorhandler(505)
def exception_handler(error):
    return abort_error_handler(AbortError('Server error', 500))

@app.errorhandler(404)
def not_found_handler(error):
    return abort_error_handler(AbortError('Not found', 404))