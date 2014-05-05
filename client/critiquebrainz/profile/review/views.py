from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from critiquebrainz.api import api
from critiquebrainz.exceptions import APIError
from critiquebrainz.forms.profile.review import CreateForm, EditForm

bp = Blueprint('profile_review', __name__)

@bp.route('/', endpoint='index')
@login_required
def index_handler():
    limit = int(request.args.get('limit', default=5))
    offset = int(request.args.get('offset', default=0))
    count, reviews = api.get_me_reviews(sort='created',
        limit=limit, offset=offset, access_token=current_user.access_token)
    return render_template('profile/review/list.html',
        reviews=reviews, limit=limit, offset=offset, count=count)

@bp.route('/write', methods=('GET', 'POST'), endpoint='create')
@login_required
def create_handler():
    release_group = request.args.get('release_group')
    if not release_group:
        flash('Please choose the album you want to review.')
        return redirect(url_for('search.selector', next=url_for('.create')))
    form = CreateForm()
    if form.validate_on_submit():
        try:
            message, id = api.create_review(release_group, form.text.data, current_user.access_token)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            flash(u'You have published the review!', 'success')
        return redirect(url_for('.index'))
    return render_template('profile/review/write.html', form=form, release_group=release_group)

@bp.route('/<uuid:id>/edit', methods=('GET', 'POST'), endpoint='edit')
@login_required
def edit_handler(id):
    review = api.get_review(str(id))
    if review.get('user_id') != current_user.me.get('id'):
        return redirect(url_for('index'))

    form = EditForm()
    if form.validate_on_submit():
        try:
            message = api.update_review(id, current_user.access_token, text=form.text.data)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            flash(u'You have modified the review!', 'success')
        return redirect(url_for('.index'))
    else:
        form.text.data = review.get('text')
    return render_template('profile/review/edit.html', form=form, review=review)

@bp.route('/<uuid:id>/delete', endpoint='delete')
@login_required
def delete_handler(id):
    try:
        message = api.delete_review(str(id), current_user.access_token)
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(u'You have deleted the review.', 'success')
    return redirect(url_for('.index'))
