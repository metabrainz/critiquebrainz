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

from flask import Blueprint, redirect, url_for
from flask_login import current_user, login_required
from flask_babel import gettext
import critiquebrainz.db.review as db_review
from critiquebrainz.frontend import flash
from critiquebrainz.frontend.forms.rate import RatingEditForm

rate_bp = Blueprint('rate', __name__)

@rate_bp.route('/', methods=['POST'])
@login_required
def rate():
    form = RatingEditForm()
    if form.validate_on_submit():
        if current_user.is_blocked:
            flash.error(gettext("You are not allowed to rate any entity because your "
                                "account has been blocked by a moderator."))
            return redirect(url_for('{}.entity'.format(form.entity_type.data), id=form.entity_id.data))
        reviews, review_count = db_review.list_reviews(
            entity_id=form.entity_id.data,
            entity_type=form.entity_type.data,
            user_id=current_user.id
        )
        review = reviews[0] if review_count else None
        if review:
            # if there is already a review
            if form.rating.data or review['text']:
                # if either rating is positive or review-text has some content, then update review to set the rating
                db_review.update(
                    review_id=review['id'],
                    drafted=review['is_draft'],
                    text=review['text'],
                    rating=form.rating.data if form.rating.data else None
                )
            else:
                # if user has cleared the rating and there was no review-text, then delete the review
                # this is because both the rating and review-text can't be None at the same time
                db_review.delete(review['id'])
        else:
            # if there is no review
            if form.rating.data:
                # if user has submitted some positive rating, then create a new review to set the rating
                db_review.create(
                    user_id=current_user.id,
                    entity_id=form.entity_id.data,
                    entity_type=form.entity_type.data,
                    rating=form.rating.data,
                    is_draft=False
                )
        flash.success("We have updated your rating for this event!")
    else:
        flash.error("Error! Could not update the rating...")
    return redirect(url_for('{}.entity'.format(form.entity_type.data), id=form.entity_id.data))
