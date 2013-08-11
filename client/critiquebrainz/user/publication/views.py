from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from critiquebrainz.api import api
from critiquebrainz.exceptions import APIError
from critiquebrainz.forms.user.publication import CreateForm, EditForm

bp = Blueprint('user_publication', __name__)

@bp.route('/', endpoint='index')
@login_required
def index_handler():
    me = api.get_me_publications(current_user.access_token)
    publications = me.get('publications')
    return render_template('user/publication/list.html',
        publications=publications)

@bp.route('/create', methods=('GET', 'POST'), endpoint='create')
@login_required
def create_handler():
    form = CreateForm()
    if form.validate_on_submit():
        try:
            message, id = api.create_publication(form.release_group.data, 
                form.text.data, current_user.access_token)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            flash(u'You have published the review!', 'success')
        return redirect(url_for('.index'))
    return render_template('user/publication/create.html', form=form)

@bp.route('/<uuid:id>/edit', methods=('GET', 'POST'), endpoint='edit')
@login_required
def edit_handler(id):
    publication = api.get_publication(str(id))
    if publication.get('user_id') != current_user.me.get('id'):
        return redirect(url_for('index'))

    form = EditForm()
    if form.validate_on_submit():
        try:
            message = api.update_publication(id, form.text.data, current_user.access_token)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            flash(u'You have modified the review!', 'success')
        return redirect(url_for('.index'))
    else:
        form.text.data = publication.get('text')
    return render_template('user/publication/edit.html', form=form, publication=publication)

@bp.route('/<uuid:id>/delete', endpoint='delete')
@login_required
def delete_handler(id):
    try:
        message = api.delete_publication(str(id), current_user.access_token)
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(u'You have deleted the review.', 'success')
    return redirect(url_for('.index'))
