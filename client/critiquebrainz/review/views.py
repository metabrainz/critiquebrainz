from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext

from critiquebrainz.apis import server, mbspotify
from critiquebrainz.exceptions import *
import markdown

bp = Blueprint('review', __name__)

@bp.route('/<uuid:id>', endpoint='entity')
def review_entity_handler(id):
    review = server.get_review(id, inc=['user'])
    spotify_mapping = mbspotify.mapping([str(review['release_group'])])
    # if user is logged in, get his vote for this review
    if current_user.is_authenticated():
        try:
            vote = server.get_vote(id, access_token=current_user.access_token)
        except APIError as e:
            # handle the exception, if user has not rated the review yet
            if e.code == 'not_found':
                vote = None
            else:
                raise e
    # otherwise set vote to None, its value will not be used
    else:
        vote = None
    review["text"] = markdown.markdown(review["text"], safe_mode="escape")
    return render_template('review/entity.html', review=review, spotify_mapping=spotify_mapping, vote=vote)

@bp.route('/<uuid:id>/vote', methods=['POST'], endpoint='vote_submit')
@login_required
def review_vote_submit_handler(id):
    if 'yes' in request.form: placet = True
    elif 'no' in request.form: placet = False
    try:
        message = server.update_review_vote(id, current_user.access_token, placet=placet)
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(gettext('You have rated the review!'), 'success')
    return redirect(url_for('.entity', id=id))

@bp.route('/<uuid:id>/vote/delete', methods=['GET'], endpoint='vote_delete')
@login_required
def review_vote_delete_handler(id):
    try:
        message = server.delete_review_vote(id, current_user.access_token)
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(gettext('You have deleted your vote for this review!'), 'success')
    return redirect(url_for('.entity', id=id))
