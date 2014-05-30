from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import login_required, current_user, logout_user
from flask.ext.babel import gettext

from critiquebrainz.apis import server
from critiquebrainz.exceptions import APIError
from critiquebrainz.forms.profile.client import ClientForm

bp = Blueprint('profile_client', __name__)

@bp.route('/', endpoint='index')
@login_required
def index_handler():
    clients = server.get_me_clients(current_user.access_token)
    tokens = server.get_me_tokens(current_user.access_token)
    return render_template('profile/client/index.html', clients=clients, tokens=tokens)

@bp.route('/create', endpoint='create', methods=['GET', 'POST'])
@login_required
def create_handler():
    form = ClientForm()
    if form.validate_on_submit():
        try:
            message, _, _ = server.create_client(form.name.data, form.desc.data,
                form.website.data, form.redirect_uri.data,
                'review vote', current_user.access_token)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            flash(gettext('You have created an API client!'), 'success')
        return redirect(url_for('.index'))
    return render_template('profile/client/create.html', form=form)

@bp.route('/<client_id>/edit', endpoint='edit', methods=['GET', 'POST'])
@login_required
def edit_handler(client_id):
    form = ClientForm()
    client = server.get_client(client_id, current_user.access_token)
    if form.validate_on_submit():
        try:
            message = server.update_client(client_id, current_user.access_token,
                name=form.name.data, desc=form.desc.data,
                website=form.website.data, redirect_uri=form.redirect_uri.data)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            flash(gettext('You have updated the API client!'), 'success')
        return redirect(url_for('.index'))
    else:
        form.name.data = client.get('name')
        form.desc.data = client.get('desc')
        form.website.data = client.get('website')
        form.redirect_uri.data = client.get('redirect_uri')
    return render_template('profile/client/edit.html', form=form)

@bp.route('/<client_id>/delete', endpoint='delete')
@login_required
def delete_handler(client_id):
    try:
        message = server.delete_client(client_id, current_user.access_token)
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(gettext('You have deleted the API client.'), 'success')
    return redirect(url_for('.index'))

@bp.route('/<client_id>/token/delete', endpoint='token_delete')
@login_required
def token_delete_handler(client_id):
    try:
        message = server.delete_token(client_id, current_user.access_token)
    except APIError as e:
        flash(e.desc, 'error')
    return redirect(url_for('.index'))

