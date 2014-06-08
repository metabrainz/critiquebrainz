from flask import render_template
from bs4 import BeautifulSoup
from markdown import markdown
from critiquebrainz import app
from critiquebrainz.apis import server
from critiquebrainz.cache import cache, generate_cache_key

DEFAULT_CACHE_EXPIRATION = 10 * 60  # seconds


@app.route('/', endpoint='index')
def index_handler():
    # User count
    user_count_key = generate_cache_key('user_count')
    user_count = cache.get(user_count_key)
    if not user_count:
        user_count, users = server.get_users(limit=1)
        cache.set(user_count_key, user_count, DEFAULT_CACHE_EXPIRATION)

    # Reviews (popular, latest) + review count
    review_count_key = generate_cache_key('review_count')
    review_count = cache.get(review_count_key)

    popular_reviews_key = generate_cache_key('popular_reviews')
    popular_reviews = cache.get(popular_reviews_key)
    if not popular_reviews or not review_count:
        review_count, popular_reviews = server.get_reviews(sort='rating', limit=6, inc=['user'])
        for review in popular_reviews:
            # Preparing text for preview
            review["text"] = markdown(review["text"], safe_mode="escape")
            review["text"] = ''.join(BeautifulSoup(review["text"]).findAll(text=True))
        cache.set(popular_reviews_key, popular_reviews, DEFAULT_CACHE_EXPIRATION)

    recent_reviews_key = generate_cache_key('recent_reviews')
    recent_reviews = cache.get(recent_reviews_key)
    if not recent_reviews or not review_count:
        review_count, recent_reviews = server.get_reviews(sort='created', limit=6, inc=['user'])
        cache.set(recent_reviews_key, recent_reviews, DEFAULT_CACHE_EXPIRATION)

    return render_template('index.html', popular_reviews=popular_reviews, recent_reviews=recent_reviews,
                           reviews_total=review_count, users_total=user_count)
