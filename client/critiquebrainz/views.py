from flask import render_template
from critiquebrainz import app
from critiquebrainz.api import api
from critiquebrainz.exceptions import APIError

@app.route('/', endpoint='index')
def index_handler():
    _, publications = api.get_publications(sort='created', limit=5, inc='user')
    return render_template('index.html', publications=publications)
