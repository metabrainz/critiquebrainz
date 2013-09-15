from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask.ext.login import login_required, current_user
from critiquebrainz.api import api
from critiquebrainz.exceptions import *

bp = Blueprint('publication', __name__)

@bp.route('/<uuid:id>', endpoint='entity')
def publication_entity_handler(id):
    publication = api.get_publication(id, include_user=True)
    # if user is logged in, get his rate of this publication
    if current_user.is_authenticated():
        try:
            rate = api.get_rate(id, access_token=current_user.access_token)
        except APIError as e:
            # handle the exception, if user has not rated the publication yet
            if e.code == 'not_found':
                rate = None
            else:
                raise e
    # otherwise set rate to None, its value will not be used
    else:
        rate = None
    return render_template('publication/entity.html', publication=publication, rate=rate)

@bp.route('/<uuid:id>/rate', methods=['POST'], endpoint='rate_submit')
@login_required
def publication_rate_submit_handler(id):
    if 'yes' in request.form: placet = True
    elif 'no' in request.form: placet = False
    try:
        message = api.update_publication_rate(id, current_user.access_token, placet=placet)
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(u'You have rated the review!', 'success')
    return redirect(url_for('.entity', id=id))

@bp.route('/<uuid:id>/rate/delete', methods=['GET'], endpoint='rate_delete')
@login_required
def publication_rate_delete_handler(id):
    try:
        message = api.delete_publication_rate(id, current_user.access_token)
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(u'You have deleted your rate for this review!', 'success')
    return redirect(url_for('.entity', id=id))
