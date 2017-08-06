from flask import Blueprint, render_template
from flask_babel import format_number
import critiquebrainz.db.users as db_users
import critiquebrainz.db.review as db_review
from bs4 import BeautifulSoup
from markdown import markdown

DEFAULT_CACHE_EXPIRATION = 10 * 60  # seconds

frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.route('/')
def index():
    # Popular reviews
    popular_reviews = db_review.get_popular(6)
    for review in popular_reviews:
        # Preparing text for preview
        preview = markdown(review['text'], safe_mode="escape")
        review['preview'] = ''.join(BeautifulSoup(preview, "html.parser").findAll(text=True))

    # Recent reviews
    recent_reviews, _ = db_review.list_reviews(sort='created', limit=9)

    # Statistics
    review_count = format_number(db_review.get_count(is_draft=False))
    user_count = format_number(db_users.total_count())

    return render_template('index/index.html', popular_reviews=popular_reviews, recent_reviews=recent_reviews,
                           reviews_total=review_count, users_total=user_count)


@frontend_bp.route('/about')
def about():
    return render_template('index/about.html')


@frontend_bp.route('/guidelines')
def guidelines():
    return render_template('index/guidelines.html')
