from flask import Blueprint, render_template, request
from flask_login import current_user
from flask_babel import gettext
from critiquebrainz.frontend.apis import musicbrainz
from critiquebrainz.data.model.review import Review
from werkzeug.exceptions import NotFound

place_bp = Blueprint('place', __name__)


@place_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    place = musicbrainz.get_place_by_id(id)
    if not place:
        raise NotFound(gettext("Sorry, we couldn't find a place with that MusicBrainz ID."))

    if current_user.is_authenticated():
        my_reviews, my_count = Review.list(entity_id=id, entity_type='place', user_id=current_user.id)
        if my_count != 0:
            my_review = my_reviews[0]
        else:
            my_review = None
    else:
        my_review = None

    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    reviews, count = Review.list(entity_id=id, entity_type='place', sort='rating', limit=limit, offset=offset)

    return render_template('place.html', id=id, place=place, reviews=reviews,
                           my_review=my_review, limit=limit, offset=offset, count=count)
