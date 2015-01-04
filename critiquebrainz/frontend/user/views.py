from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

from critiquebrainz.data.model.user import User
from critiquebrainz.data.model.review import Review

user_bp = Blueprint('user', __name__)


@user_bp.route('/<uuid:user_id>')
def reviews(user_id):
    user_id = str(user_id)
    if current_user.is_authenticated() and current_user.id == user_id:
        user = current_user
    else:
        user = User.query.get_or_404(user_id)
    page = int(request.args.get('page', default=1))
    if page < 1:
        return redirect(url_for('.reviews'))
    limit = 12
    offset = (page - 1) * limit
    reviews, count = Review.list(user_id=user_id, sort='created', limit=limit, offset=offset,
                                 include_drafts=current_user.is_authenticated() and current_user.id == user_id)
    return render_template('user/reviews.html', section='reviews', user=user,
                           reviews=reviews, page=page, limit=limit, count=count)


@user_bp.route('/<uuid:user_id>/info')
def info(user_id):
    return render_template('user/info.html', section='info', user=User.query.get_or_404(str(user_id)))
