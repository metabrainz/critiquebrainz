# critiquebrainz - Repository for Creative Commons licensed reviews
#
# Copyright (C) 2018 MetaBrainz Foundation Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from flask import Blueprint, render_template, request, redirect, url_for
from flask_babel import gettext
from flask_login import current_user
from werkzeug.exceptions import NotFound, BadRequest

import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.musicbrainz_db.place as mb_place
import critiquebrainz.frontend.external.musicbrainz_db.event as mb_event
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.views import get_avg_rating, PLACE_REVIEW_LIMIT, BROWSE_EVENTS_LIMIT

place_bp = Blueprint('place', __name__)


@place_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    place = mb_place.get_place_by_mbid(id)
    if place is None:
        raise NotFound(gettext("Sorry, we couldn't find a place with that MusicBrainz ID."))

    place_review_limit = PLACE_REVIEW_LIMIT
    if request.args.get('reviews') == "all":
        place_review_limit = None

    if current_user.is_authenticated:
        my_reviews, _ = db_review.list_reviews(
            entity_id=place['mbid'],
            entity_type='place',
            user_id=current_user.id
        )
        my_review = my_reviews[0] if my_reviews else None
    else:
        my_review = None

    rating_form = RatingEditForm(entity_id=id, entity_type='place')
    rating_form.rating.data = my_review['rating'] if my_review else None
    
    reviews_offset = 0
    reviews, reviews_count = db_review.list_reviews(
        entity_id=place['mbid'],
        entity_type='place',
        sort='popularity',
        limit=place_review_limit,
        offset=reviews_offset,
    )
    avg_rating = get_avg_rating(place['mbid'], "place")

    event_type = request.args.get('event_type', default='concert')
    if event_type not in ['concert', 'festival', 'other']:  # supported event types
        raise BadRequest("Unsupported event type.")

    includeNullType = False
    if event_type == 'other':
        event_types = ['award ceremony', 'convention/expo', 'launch event', 'masterclass/clinic', 'stage performance']
        includeNullType = True
    else: 
        event_types = [event_type]

    try:
        page = int(request.args.get('page', default=1))
    except ValueError:
        raise BadRequest("Invalid page number!")
    
    if page < 1:
        return redirect(url_for('place.entity', id=id))

    events_offset = (page - 1) * BROWSE_EVENTS_LIMIT
    events, events_count = mb_event.get_event_for_place(
        place_id=place['mbid'],
        event_types=event_types,
        limit=BROWSE_EVENTS_LIMIT,
        offset=events_offset,
        includeNullType=includeNullType,
    )
    
    return render_template(
        'place/entity.html',
        id=place['mbid'],
        place=place,
        events=events,
        event_type=event_type,
        page=page,
        events_limit=BROWSE_EVENTS_LIMIT,
        events_count=events_count,
        reviews=reviews,
        rating_form=rating_form,
        my_review=my_review,
        reviews_limit=place_review_limit,
        reviews_count=reviews_count,
        avg_rating=avg_rating,
        current_user=current_user
    )
