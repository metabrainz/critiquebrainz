from flask import render_template
from critiquebrainz import app
from critiquebrainz.api import api


@app.route('/', endpoint='index')
def index_handler():
    count, hot_reviews = api.get_reviews(sort='rating', limit=5, inc=['user'])
    reviews_total, recent_reviews = api.get_reviews(sort='created', limit=5, inc=['user'])
    users_total, users = api.get_users(limit=1)
    return render_template('index.html', hot_reviews=hot_reviews, recent_reviews=recent_reviews,
                           reviews_total=reviews_total, users_total=users_total)
