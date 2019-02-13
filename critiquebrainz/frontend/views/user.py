from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.exceptions import NotFound
from flask_babel import gettext
from flask_login import login_required, current_user
from critiquebrainz.db.moderation_log import AdminActions
from critiquebrainz.db.user import User
from critiquebrainz.frontend.forms.log import AdminActionForm
from critiquebrainz.frontend.login import admin_view
from critiquebrainz.frontend import flash
import critiquebrainz.db.users as db_users
import critiquebrainz.db.review as db_review
import critiquebrainz.db.moderation_log as db_moderation_log

user_bp = Blueprint('user', __name__)


@user_bp.route('/<uuid:user_id>')
def reviews(user_id):
    user_id = str(user_id)
    if current_user.is_authenticated and current_user.id == user_id:
        user = current_user
    else:
        user = db_users.get_by_id(user_id)
        if not user:
            raise NotFound("Can't find a user with ID: {user_id}".format(user_id=user_id))
        user = User(user)
    page = int(request.args.get('page', default=1))
    if page < 1:
        return redirect(url_for('.reviews'))
    limit = 12
    offset = (page - 1) * limit
    reviews, count = db_review.list_reviews(user_id=user_id, sort='published_on', limit=limit, offset=offset,
                                            inc_hidden=current_user.is_admin(),
                                            inc_drafts=current_user.is_authenticated and current_user.id == user_id)
    return render_template('user/reviews.html', section='reviews', user=user,
                           reviews=reviews, page=page, limit=limit, count=count)


@user_bp.route('/<uuid:user_id>/info')
def info(user_id):
    user = db_users.get_by_id(user_id)
    if not user:
        raise NotFound("Can't find a user with ID: {user_id}".format(user_id=user_id))
    user = User(user)
    return render_template('user/info.html', section='info', user=user)


@user_bp.route('/<uuid:user_id>/block', methods=['GET', 'POST'])
@login_required
@admin_view
def block(user_id):
    user = db_users.get_by_id(user_id)
    if not user:
        raise NotFound("Can't find a user with ID: {user_id}".format(user_id=user_id))

    if user['is_blocked']:
        flash.info(gettext("This account is already blocked."))
        return redirect(url_for('user.reviews', user_id=user['id']))

    form = AdminActionForm()
    if form.validate_on_submit():
        db_users.block(user['id'])
        db_moderation_log.create(admin_id=current_user.id, action=AdminActions.ACTION_BLOCK_USER,
                                 reason=form.reason.data, user_id=user['id'])
        flash.success(gettext("This user account has been blocked."))
        return redirect(url_for('user.reviews', user_id=user['id']))

    return render_template('log/action.html', user=user, form=form, action=AdminActions.ACTION_BLOCK_USER.value)


@user_bp.route('/<uuid:user_id>/unblock', methods=['GET', 'POST'])
@login_required
@admin_view
def unblock(user_id):
    user = db_users.get_by_id(user_id)
    if not user:
        raise NotFound("Can't find a user with ID: {user_id}".format(user_id=user_id))

    if not user['is_blocked']:
        flash.info(gettext("This account is not blocked."))
        return redirect(url_for('user.reviews', user_id=user['id']))

    form = AdminActionForm()
    if form.validate_on_submit():
        db_users.unblock(user['id'])
        db_moderation_log.create(admin_id=current_user.id, action=AdminActions.ACTION_UNBLOCK_USER,
                                 reason=form.reason.data, user_id=user['id'])
        flash.success(gettext("This user account has been unblocked."))
        return redirect(url_for('user.reviews', user_id=user['id']))

    return render_template('log/action.html', user=user, form=form, action=AdminActions.ACTION_UNBLOCK_USER.value)
