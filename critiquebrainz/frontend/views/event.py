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

from itertools import groupby
from operator import itemgetter

from flask import Blueprint, render_template, request
from flask_babel import gettext
from flask_login import current_user
from werkzeug.exceptions import NotFound

import critiquebrainz.db.review as db_review
import critiquebrainz.frontend.external.musicbrainz_db.event as mb_event
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
from critiquebrainz.frontend.forms.rate import RatingEditForm
from critiquebrainz.frontend.views import get_avg_rating

event_bp = Blueprint('event', __name__)


@event_bp.route('/<uuid:id>')
def entity(id):
    id = str(id)
    try:
        event = mb_event.get_event_by_id(id)
    except mb_exceptions.NoDataFoundException:
        raise NotFound(gettext("Sorry, we couldn't find an event with that MusicBrainz ID."))

    if 'url-rels' in event:
        external_reviews = list(filter(lambda rel: rel['type'] == 'review', event['url-rels']))
    else:
        external_reviews = []

    if 'artist-rels' in event and event['artist-rels']:
        artists_unique = []
        for artist in event['artist-rels']:
            if artist not in artists_unique:
                artists_unique.append(artist)
        artists_sorted = sorted(artists_unique, key=itemgetter('type'))
        event['artists_grouped'] = groupby(artists_sorted, itemgetter('type'))

    if current_user.is_authenticated:
        my_reviews, _ = db_review.list_reviews(
            entity_id=event['id'],
            entity_type='event',
            user_id=current_user.id
        )
        my_review = my_reviews[0] if my_reviews else None
    else:
        my_review = None

    rating_form = RatingEditForm(entity_id=id, entity_type='event')
    rating_form.rating.data = my_review['rating'] if my_review else None

    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    reviews, count = db_review.list_reviews(
        entity_id=event['id'],
        entity_type='event',
        sort='popularity',
        limit=limit,
        offset=offset
    )
    avg_rating = get_avg_rating(event['id'], "event")

    return render_template('event/entity.html', id=event['id'], event=event, reviews=reviews,
                           rating_form=rating_form, my_review=my_review, external_reviews=external_reviews,
                           limit=limit, offset=offset, count=count, avg_rating=avg_rating, current_user=current_user)
