from flask import render_template
from critiquebrainz import app
from critiquebrainz.api import api


@app.route('/', endpoint='index')
def index_handler():
    _, hot_reviews = api.get_reviews(sort='rating', limit=5, inc=['user'])
    _, recent_reviews = api.get_reviews(sort='created', limit=5, inc=['user'])
    return render_template('index.html', hot_reviews=hot_reviews, recent_reviews=recent_reviews)
