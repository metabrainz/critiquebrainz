from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from critiquebrainz.api import api
from critiquebrainz.exceptions import APIError
from critiquebrainz.forms.user.publication import CreateForm, EditForm

bp = Blueprint('user_publication', __name__)

@bp.route('/', endpoint='index')
@login_required
def index_handler():
    error, me = api.get_me_publications(current_user.access_token)
    if error:
        raise APIError(error)
    publications = me.get('publications')
    return render_template('user/publication/list.html',
        publications=publications)

@bp.route('/create', methods=('GET', 'POST'), endpoint='create')
@login_required
def create_handler():
    form = CreateForm()
    if form.validate_on_submit():
        error, message, id = api.create_publication(form.release_group.data, 
            form.text.data, current_user.access_token)
        if error:
            raise APIError(error)
        flash(message)
        return redirect(url_for('.index'))
    return render_template('user/publication/create.html', form=form)

@bp.route('/<uuid:id>/edit', methods=('GET', 'POST'), endpoint='edit')
@login_required
def edit_handler(id):
    error, publication = api.get_publication(str(id))
    if error:
        raise APIError(error)
    if publication.get('user_id') != current_user.me.get('id'):
        return redirect(url_for('index'))

    form = EditForm()
    if form.validate_on_submit():
        error, message = api.update_publication(id, form.text.data, current_user.access_token)
        if error:
            raise APIError(error)
        flash(message)
        return redirect(url_for('.index'))
    else:
        form.text.data = publication.get('text')
    return render_template('user/publication/edit.html', form=form, publication=publication)

@bp.route('/<uuid:id>/delete', endpoint='delete')
@login_required
def delete_handler(id):
    error, message = api.delete_publication(str(id), current_user.access_token)
    if error:
        raise APIError(error)
    flash(message)
    return redirect(url_for('.index'))
