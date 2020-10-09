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

from flask import Blueprint, redirect, url_for, render_template, request
from flask_babel import gettext
from flask_login import current_user, login_required
from markdown import markdown
from werkzeug.exceptions import Unauthorized, NotFound

import critiquebrainz.db.comment as db_comment
from critiquebrainz.db import exceptions as db_exceptions
from critiquebrainz.frontend import flash
from critiquebrainz.frontend.forms.comment import CommentEditForm
from critiquebrainz.frontend.views.review import get_review_or_404

comment_bp = Blueprint('comment', __name__)


def get_comment_or_404(comment_id):
    """Get a comment using comment ID or raise error 404."""
    try:
        return db_comment.get_by_id(comment_id)
    except db_exceptions.NoDataFoundException:
        raise NotFound(gettext("Can't find a comment with ID: %(comment_id)s", comment_id=comment_id))


@comment_bp.route('/create', methods=['POST'])
@login_required
def create():
    # TODO (code-master5): comment limit, revision and drafts, edit functionality
    form = CommentEditForm()
    if form.validate_on_submit():
        get_review_or_404(form.review_id.data)
        if current_user.is_blocked:
            flash.error(gettext("You are not allowed to write new comments because your "
                                "account has been blocked by a moderator."))
            return redirect(url_for('review.entity', id=form.review_id.data))
        # should be able to comment only if review exists
        db_comment.create(
            review_id=form.review_id.data,
            user_id=current_user.id,
            text=form.text.data,
        )
        flash.success(gettext("Comment has been saved!"))
    elif not form.text.data:
        # comment must have some text
        flash.error(gettext("Comment must not be empty!"))
    return redirect(url_for('review.entity', id=form.review_id.data))


@comment_bp.route('/<uuid:id>/delete', methods=['GET', 'POST'])
@login_required
def delete(id):
    comment = get_comment_or_404(id)
    # if comment exists, review must exist
    review = get_review_or_404(comment["review_id"])
    if comment["user"] != current_user:
        raise Unauthorized(gettext("Only the author can delete this comment."))
    if request.method == 'POST':
        db_comment.delete(comment["id"])
        flash.success(gettext("Comment has been deleted."))
        return redirect(url_for('review.entity', id=comment["review_id"]))
    if comment:
        comment["text_html"] = markdown(comment["last_revision"]["text"], safe_mode="escape")
    return render_template('review/delete_comment.html', review=review, comment=comment)


@comment_bp.route('/<uuid:id>/edit', methods=['POST'])
@login_required
def edit(id):
    comment = get_comment_or_404(id)
    if comment["user"] != current_user:
        raise Unauthorized(gettext("Only the author can edit this comment."))
    if current_user.is_blocked:
        flash.error(gettext("You are not allowed to edit comments because your "
                            "account has been blocked by a moderator."))
        return redirect(url_for('review.entity', id=comment["review_id"]))
    form = CommentEditForm()
    if form.validate_on_submit():
        if form.text.data != comment["last_revision"]["text"]:
            db_comment.update(
                comment_id=comment["id"],
                text=form.text.data
            )
            flash.success(gettext("Comment has been updated."))
        else:
            flash.error(gettext("You must change some content of the comment to update it!"))
    elif not form.text.data:
        # comment must have some text
        flash.error(gettext("Comment must not be empty!"))
    return redirect(url_for('review.entity', id=comment["review_id"]))
