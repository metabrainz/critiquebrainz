from flask import Blueprint, render_template, request
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext

from critiquebrainz.apis import server
from critiquebrainz.exceptions import ServerError, NotFound

bp = Blueprint('user', __name__)


def get_user(user_id, inc=[]):
    try:
        return server.get_user(user_id, inc=inc)
    except ServerError as e:
        if e.code == 'not_found':
            raise NotFound(gettext("Sorry we couldn't find user with that ID."))
        else:
            raise e


@bp.route('/<uuid:user_id>', endpoint='profile')
def profile_handler(user_id):
    return render_template('user/profile.html', section='profile', user=get_user(user_id, ['user_type', 'stats']))


@bp.route('/<uuid:user_id>/reviews', endpoint='reviews')
def reviews_handler(user_id):
    if current_user.is_authenticated() and current_user.me['id'] == user_id:
        user = current_user.me
    else:
        user = get_user(user_id)
    offset = int(request.args.get('offset', default=0))
    limit = 10
    count, reviews = server.get_reviews(user_id=user_id, sort='created', limit=limit, offset=offset)
    return render_template('user/reviews.html', section='reviews', user=user,
                           reviews=reviews, limit=limit, offset=offset, count=count)
