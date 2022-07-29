from flask import Blueprint, render_template, request
from flask_login import current_user
from werkzeug.exceptions import NotFound, BadRequest
from flask_babel import gettext
import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.bookbrainz_db.publisher as bb_publisher
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.views import get_avg_rating, PUBLISHER_REVIEWS_LIMIT
from datetime import datetime

bb_publisher_bp = Blueprint('bb_publisher', __name__)


@bb_publisher_bp.route('/<uuid:id>')
def entity(id):
	id = str(id)
	publisher = bb_publisher.get_publisher_by_bbid(id)

	if publisher is None:
		raise NotFound(gettext("Sorry, we couldn't find a publisher with that BookBrainz ID."))

	try:
		reviews_limit = int(request.args.get('limit', default=PUBLISHER_REVIEWS_LIMIT))
	except ValueError:
		raise BadRequest("Invalid limit parameter!")

	try:
		reviews_offset = int(request.args.get('offset', default=0))
	except ValueError:
		raise BadRequest("Invalid offset parameter!")

	if current_user.is_authenticated:
		my_reviews, _ = db_review.list_reviews(
			entity_id=publisher['bbid'],
			entity_type='bb_publisher',
			user_id=current_user.id,
		)
		my_review = my_reviews[0] if my_reviews else None
	else:
		my_review = None
	reviews, count = db_review.list_reviews(
		entity_id=publisher['bbid'],
		entity_type='bb_publisher',
		sort='popularity',
		limit=reviews_limit,
		offset=reviews_offset,
	)
	avg_rating = get_avg_rating(publisher['bbid'], "bb_publisher")

	rating_form = RatingEditForm(entity_id=id, entity_type='bb_publisher')
	rating_form.rating.data = my_review['rating'] if my_review else None

	if publisher['begin_day'] and publisher['begin_month'] and publisher['begin_year']:
		begin_date = datetime(publisher['begin_year'], publisher['begin_month'], publisher['begin_day'])
	else:
		begin_date = None

	if publisher['end_day'] and publisher['end_month'] and publisher['end_year']:
		end_date = datetime(publisher['end_year'], publisher['end_month'], publisher['end_day'])
	else:
		end_date = None
	

	return render_template('bb_publisher/entity.html',
						   id=publisher['bbid'],
						   publisher=publisher,
						   reviews=reviews,
						   begin_date=begin_date,
						   end_date=end_date,
						   my_review=my_review,
						   count=count,
						   rating_form=rating_form,
						   current_user=current_user,
						   limit=reviews_limit,
						   offset=reviews_offset,
						   avg_rating=avg_rating)