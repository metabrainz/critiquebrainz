from flask import Blueprint, render_template
from flask_babel import format_number
from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.review import Review
from bs4 import BeautifulSoup
from markdown import markdown

DEFAULT_CACHE_EXPIRATION = 10 * 60  # seconds

frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.route('/', endpoint='index')
def index_handler():
    # Popular reviews
    popular_reviews, _ = Review.list(sort='rating', limit=6)
    for review in popular_reviews:
        # Preparing text for preview
        preview = markdown(review.text, safe_mode="escape")
        review.preview = ''.join(BeautifulSoup(preview).findAll(text=True))

    # Recent reviews
    recent_reviews, _ = Review.list(sort='created', limit=6)

    # Getting counts and formatting them
    review_count = format_number(Review.query.filter(Review.is_archived == False).filter(Review.is_draft == False).count())
    user_count = format_number(User.query.count())

    return render_template('index.html', popular_reviews=popular_reviews, recent_reviews=recent_reviews,
                           reviews_total=review_count, users_total=user_count)


@frontend_bp.route('/about', endpoint='about')
def about_page():
    return render_template('about.html')
