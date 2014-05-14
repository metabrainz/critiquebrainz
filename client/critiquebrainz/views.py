from flask import render_template
from critiquebrainz import app
from critiquebrainz.api import api
from critiquebrainz.cache import cache, generate_cache_key

DEFAULT_CACHE_EXPIRATION = 10 * 60  # seconds

@app.route('/', endpoint='index')
def index_handler():
    # User count
    user_count_key = generate_cache_key('user_count')
    user_count = cache.get(user_count_key)
    if not user_count:
        count, users = api.get_users(limit=1)
        cache.set(user_count_key, count, DEFAULT_CACHE_EXPIRATION)

    # Reviews (hot, latest) + review count
    review_count_key = generate_cache_key('review_count')
    review_count = cache.get(review_count_key)

    hot_reviews_key = generate_cache_key('hot_reviews')
    hot_reviews = cache.get(hot_reviews_key)
    if not hot_reviews:
        count, hot_reviews = api.get_reviews(sort='rating', limit=5, inc=['user'])
        cache.set(hot_reviews_key, hot_reviews, DEFAULT_CACHE_EXPIRATION)
        if not review_count:
            review_count = count
            cache.set(review_count_key, review_count, DEFAULT_CACHE_EXPIRATION)

    recent_reviews_key = generate_cache_key('recent_reviews')
    recent_reviews = cache.get(recent_reviews_key)
    if not recent_reviews:
        count, recent_reviews = api.get_reviews(sort='created', limit=5, inc=['user'])
        cache.set(recent_reviews_key, recent_reviews, DEFAULT_CACHE_EXPIRATION)
        if not review_count:
            review_count = count
            cache.set(review_count_key, review_count, DEFAULT_CACHE_EXPIRATION)

    return render_template('index.html', hot_reviews=hot_reviews, recent_reviews=recent_reviews,
                           reviews_total=review_count, users_total=user_count)
