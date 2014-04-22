from flask import render_template
from critiquebrainz import app
from critiquebrainz.api import api
from critiquebrainz.exceptions import APIError

@app.route('/', endpoint='index')
def index_handler():
    _, reviews = api.get_reviews(sort='created', limit=5, inc=['user'])
    return render_template('index.html', reviews=reviews)
