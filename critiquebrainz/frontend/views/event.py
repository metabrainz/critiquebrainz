from itertools import groupby
from operator import itemgetter
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user
from flask_babel import gettext
from werkzeug.exceptions import NotFound
import critiquebrainz.db.review as db_review
from critiquebrainz.frontend import flash
import critiquebrainz.frontend.external.musicbrainz_db.event as mb_event
import critiquebrainz.frontend.external.musicbrainz_db.exceptions as mb_exceptions
from critiquebrainz.frontend.forms.rate import RatingForm
from critiquebrainz.frontend.views import get_avg_rating


event_bp = Blueprint('event', __name__)


@event_bp.route('/<uuid:id>', methods=['GET', 'POST'])
def entity(id):
    id = str(id)
    try:
        event = mb_event.get_event_by_id(id)
    except mb_exceptions.NoDataFoundException:
        raise NotFound(gettext("Sorry, we couldn't find an event with that MusicBrainz ID."))

    if 'artist-rels' in event and event['artist-rels']:
        artists_sorted = sorted(event['artist-rels'], key=itemgetter('type'))
        event['artists_grouped'] = groupby(artists_sorted, itemgetter('type'))

    if current_user.is_authenticated:
        my_reviews, my_count = db_review.list_reviews(entity_id=event['id'], entity_type='event', user_id=current_user.id)
        if my_count != 0:
            my_review = my_reviews[0]
        else:
            my_review = None
    else:
        my_review = None

    form = RatingForm()

    if form.validate_on_submit():
        if my_review:
            # if there is already a review
            if form.rating.data or my_review['text']:
                # if either rating is positive or review-text has some content, then update review to set the rating
                db_review.update(review_id=my_review['id'], drafted=my_review['is_draft'], text=my_review['text'],
                                 rating=form.rating.data if form.rating.data else None)
            else:
                # if user has cleared the rating and there was no review-text, then delete the review
                # this is because both the rating and review-text can't be None at the same time
                db_review.delete(my_review['id'])
        else:
            # if there is no review
            if form.rating.data:
                # user has submitted some positive rating, then create a new review to set the rating
                db_review.create(user_id=current_user.id, entity_id=id, entity_type='event',
                                 rating=form.rating.data, is_draft=False)
        flash.success("We have updated your rating for this event!".format(form.rating.data))
        return redirect(url_for('.entity', id=event['id']))

    form.rating.data = my_review['rating'] if my_review else None
    limit = int(request.args.get('limit', default=10))
    offset = int(request.args.get('offset', default=0))
    reviews, count = db_review.list_reviews(entity_id=event['id'], entity_type='event', sort='popularity',
                                            limit=limit, offset=offset)
    avg_rating = get_avg_rating(event['id'], "event")

    return render_template('event/entity.html', id=event['id'], event=event, reviews=reviews, form=form,
                           my_review=my_review, limit=limit, offset=offset, count=count, avg_rating=avg_rating,
                           current_user=current_user)
