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
from critiquebrainz.frontend import flash
from critiquebrainz.frontend.forms.comment import CommentEditForm

import critiquebrainz.db.comment as db_comment

comment_bp = Blueprint('comment', __name__)


@comment_bp.route('/create', methods=['POST'])
@login_required
def create():
    form = CommentEditForm()
    if form.validate_on_submit():
        comment = db_comment.create(
            review_id=form.review_id.data,
            user_id=current_user.id,
            text=form.text.data,
        )
        flash.success('Comment has been saved!')
    return redirect(url_for('review.entity', id=comment['review_id']))
