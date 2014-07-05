from flask import Blueprint, render_template, request
from flask.ext.babel import gettext

from critiquebrainz.apis import server
from critiquebrainz.exceptions import ServerError, NotFound

bp = Blueprint('user', __name__)

@bp.route('/<uuid:id>', endpoint='entity')
def user_entity_handler(id):
    try:
        user = server.get_user(id, inc=['user_type', 'stats'])
    except ServerError as e:
        if e.code == 'not_found':
            raise NotFound(gettext("Sorry we couldn't find user with that ID."))
        else:
            raise e
    limit = int(request.args.get('limit', default=5))
    offset = int(request.args.get('offset', default=0))
    count, reviews = server.get_reviews(user_id=id, sort='created', limit=limit, offset=offset)
    return render_template('user/entity.html', user=user, reviews=reviews, limit=limit, offset=offset, count=count)
