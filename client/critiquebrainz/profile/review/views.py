from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext

from critiquebrainz.apis import server
from critiquebrainz.exceptions import APIError
from critiquebrainz.forms.profile.review import ReviewCreateForm, ReviewEditForm
import markdown

bp = Blueprint('profile_review', __name__)

@bp.route('/', endpoint='index')
@login_required
def index_handler():
    limit = int(request.args.get('limit', default=5))
    offset = int(request.args.get('offset', default=0))
    count, reviews = server.get_me_reviews(sort='created',
        limit=limit, offset=offset, access_token=current_user.access_token)
    return render_template('profile/review/list.html',
        reviews=reviews, limit=limit, offset=offset, count=count)

@bp.route('/write', methods=('GET', 'POST'), endpoint='create')
@login_required
def create_handler():
    release_group = request.args.get('release_group')
    if not release_group:
        flash('Please choose release group that you want to review.')
        return redirect(url_for('search.selector', next=url_for('.create')))
    form = ReviewCreateForm(license_choice='CC BY-SA 3.0')
    if form.validate_on_submit():
        try:
            server.create_review(release_group, form.text.data, form.license_choice.data, form.language.data, current_user.access_token)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            flash(gettext('You have published the review!'), 'success')
        return redirect(url_for('.index'))
    return render_template('profile/review/write.html', form=form, release_group=release_group)

@bp.route('/write/preview', methods=['POST'], endpoint='preview')
@login_required
def preview_handler():
    """Get markdown preview of a text."""
    return markdown.markdown(request.form['text'], safe_mode="escape")

@bp.route('/<uuid:id>/edit', methods=('GET', 'POST'), endpoint='edit')
@login_required
def edit_handler(id):
    review = server.get_review(str(id))
    if review.get('user_id') != current_user.me.get('id'):
        return redirect(url_for('index'))

    form = ReviewEditForm()
    if form.validate_on_submit():
        try:
            message = server.update_review(id, current_user.access_token, text=form.text.data)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            flash(gettext('You have modified the review!'), 'success')
        return redirect(url_for('.index'))
    else:
        form.text.data = review.get('text')
    return render_template('profile/review/edit.html', form=form, review=review)

@bp.route('/<uuid:id>/delete', endpoint='delete')
@login_required
def delete_handler(id):
    try:
        message = server.delete_review(str(id), current_user.access_token)
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(gettext('You have deleted the review.'), 'success')
    return redirect(url_for('.index'))
