from datetime import datetime
from flask import Blueprint, render_template, request
from flask_login import current_user
from werkzeug.exceptions import NotFound, BadRequest
from flask_babel import gettext
import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.bookbrainz_db.author as bb_author
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.views import get_avg_rating, AUTHOR_REVIEWS_LIMIT

bb_author_bp = Blueprint('bb_author', __name__)

@bb_author_bp.route('/<uuid:id>')
def entity(id):
	id = str(id)
	author = bb_author.get_author_by_bbid(id)

	if author is None:
		raise NotFound(gettext("Sorry, we couldn't find an author with that BookBrainz ID."))

	try:
		reviews_limit = int(request.args.get('limit', default=AUTHOR_REVIEWS_LIMIT))
	except ValueError:
		raise BadRequest("Invalid limit parameter!")

	try:
		reviews_offset = int(request.args.get('offset', default=0))
	except ValueError:
		raise BadRequest("Invalid offset parameter!")

	if current_user.is_authenticated:
		my_reviews, _ = db_review.list_reviews(
			entity_id=author['bbid'],
			entity_type='bb_author',
			user_id=current_user.id,
		)
		my_review = my_reviews[0] if my_reviews else None
	else:
		my_review = None

	reviews, count = db_review.list_reviews(
		entity_id=author['bbid'],
		entity_type='bb_author',
		sort='popularity',
		limit=reviews_limit,
		offset=reviews_offset,
	)
	avg_rating = get_avg_rating(author['bbid'], "bb_author")

	rating_form = RatingEditForm(entity_id=id, entity_type='bb_author')
	rating_form.rating.data = my_review['rating'] if my_review else None

	if author['begin_day'] and author['begin_month'] and author['begin_year']:
		begin_date = datetime(author['begin_year'], author['begin_month'], author['begin_day'])
	else:
		begin_date = None

	if author['end_day'] and author['end_month'] and author['end_year']:
		end_date = datetime(author['end_year'], author['end_month'], author['end_day'])
	else:
		end_date = None

	begin_area = None
	end_area = None
	for area in author['area_info']:
		if author['begin_area_id'] and author['begin_area_id'] == area['id']:
			begin_area = area
		if author['end_area_id'] and author['end_area_id'] == area['id']:
			end_area = area


	return render_template('bb_author/entity.html',
						   id=author['bbid'],
						   author=author,
						   begin_date=begin_date,
						   end_date=end_date,
						   begin_area=begin_area,
						   end_area=end_area,
						   reviews=reviews,
						   my_review=my_review,
						   count=count,
						   rating_form=rating_form,
						   current_user=current_user,
						   limit=reviews_limit,
						   offset=reviews_offset,
						   avg_rating=avg_rating)
