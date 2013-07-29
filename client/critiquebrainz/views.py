from flask import render_template
from critiquebrainz import app
from critiquebrainz.exceptions import OAuthError

@app.route('/', endpoint='index')
def index_handler():
    return render_template('base.html')

@app.errorhandler(OAuthError)
def oauth_error_handler(error):
    return render_template('error.html', code=error.code, description=error.description)
