from flask import redirect, url_for, render_template, flash
from flask.ext.login import logout_user
from flask.ext.babel import gettext

from critiquebrainz.exceptions import APIError
from critiquebrainz import app


@app.errorhandler(APIError)
def api_error_handler(error):
    if error.code in ('invalid_token', 'invalid_grant'):
        # logout, if the user is logged in with an invalid access and/or refresh token
        logout_user()
        flash(gettext('Your login session has expired. Please sign in again.'), 'error')
        return redirect(url_for('index'))
    else:
        return exception_handler(error)


@app.errorhandler(404)
def not_found_handler(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def exception_handler(error):
    return render_template('errors/500.html', error=error), 500


@app.errorhandler(503)
def exception_handler(error):
    return render_template('errors/503.html', error=error), 503



