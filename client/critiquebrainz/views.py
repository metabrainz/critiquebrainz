from flask import render_template
from critiquebrainz import app
from critiquebrainz.exceptions import APIError

@app.route('/', endpoint='index')
def index_handler():
    return render_template('base.html')
