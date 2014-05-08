from critiquebrainz.exceptions import APIError
from critiquebrainz import app
from flask import redirect, url_for, render_template, abort, flash
from flask.ext.login import logout_user

@app.errorhandler(APIError)
def api_error_handler(error):
    if error.code in ('invalid_token', 'invalid_grant'):
        # logout, if the user is logged in with an invalid access and/or refresh token
        logout_user()
        flash('Your login session has expired. Please sign in again.', 'error')
        return redirect(url_for('index'))
    else:
        return render_template('error.html', code=error.code, description=error.desc), error.status

@app.errorhandler(404)
def not_found_handler(error):
    return render_template('error.html', code='404', description='Requested page was not found'), 404

@app.errorhandler(500)
def exception_handler(error):
    return render_template('error.html', code='500', description='Oops! Server could not complete the request. Please try again later.'), 500

