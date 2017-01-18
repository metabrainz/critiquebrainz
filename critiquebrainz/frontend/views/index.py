from flask import Blueprint, render_template
from flask_babel import format_number
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.review import Review
from bs4 import BeautifulSoup
from markdown import markdown

DEFAULT_CACHE_EXPIRATION = 10 * 60  # seconds

frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.route('/')
def index():
    # Popular reviews
    popular_reviews = Review.get_popular(6)
    for review in popular_reviews:
        # Preparing text for preview
        preview = markdown(review['text'], safe_mode="escape")
        review['preview'] = ''.join(BeautifulSoup(preview, "html.parser").findAll(text=True))

    # Recent reviews
    recent_reviews, _ = Review.list(sort='created', limit=9)

    # Statistics
    review_count = format_number(Review.get_count(is_draft = False))
    user_count = format_number(User.get_count())

    return render_template('index/index.html', popular_reviews=popular_reviews, recent_reviews=recent_reviews,
                           reviews_total=review_count, users_total=user_count)


@frontend_bp.route('/about')
def about():
    return render_template('index/about.html')
