from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask.ext.login import login_required, current_user
from critiquebrainz.api import api
from critiquebrainz.exceptions import *

bp = Blueprint('user', __name__)

@bp.route('/<uuid:id>', endpoint='entity')
def user_entity_handler(id):
    user = api.get_user(id, inc=['user_type', 'stats'])
    limit = int(request.args.get('limit', default=5))
    offset = int(request.args.get('offset', default=0))
    count, publications = api.get_publications(user_id=id, sort='created',
        limit=limit, offset=offset)
    return render_template('user/entity.html', user=user, publications=publications,
        limit=limit, offset=offset, count=count)
