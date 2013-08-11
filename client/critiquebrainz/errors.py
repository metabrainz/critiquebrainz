from critiquebrainz.exceptions import APIError
from critiquebrainz import app
from flask import render_template, abort

@app.errorhandler(404)
def not_found_handler(error):
    return render_template('error.html', code='404', description='Requested page was not found'), 404

@app.errorhandler(500)
def exception_handler(error):
    return render_template('error.html', code='500', description='Oops! Server could not complete the request. Please try again later.'), 500

@app.errorhandler(APIError)
def api_error_handler(error):
    return render_template('error.html', code=error.code, description=error.desc), error.status
