from flask import Blueprint, render_template, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext

from critiquebrainz.apis import server
from critiquebrainz.exceptions import APIError
from critiquebrainz.forms.profile.client import ClientForm

profile_apps_bp = Blueprint('profile_applications', __name__)


@profile_apps_bp.route('/', endpoint='index')
@login_required
def index_handler():
    applications = server.get_me_applications(current_user.access_token)
    tokens = server.get_me_tokens(current_user.access_token)
    return render_template('profile/applications/index.html', applications=applications, tokens=tokens)


@profile_apps_bp.route('/create', endpoint='create', methods=['GET', 'POST'])
@login_required
def create_handler():
    """Create application."""
    form = ClientForm()
    if form.validate_on_submit():
        try:
            server.create_application(form.name.data, form.desc.data, form.website.data, form.redirect_uri.data, current_user.access_token)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            flash(gettext('You have created an application!'), 'success')
        return redirect(url_for('.index'))
    return render_template('profile/applications/create.html', form=form)


@profile_apps_bp.route('/<client_id>/edit', endpoint='edit', methods=['GET', 'POST'])
@login_required
def edit_handler(client_id):
    form = ClientForm()
    application = server.get_application(client_id, current_user.access_token)
    if form.validate_on_submit():
        try:
            message = server.update_application(client_id, current_user.access_token,
                name=form.name.data, desc=form.desc.data,
                website=form.website.data, redirect_uri=form.redirect_uri.data)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            flash(gettext('You have updated an application!'), 'success')
        return redirect(url_for('.index'))
    else:
        form.name.data = application.get('name')
        form.desc.data = application.get('desc')
        form.website.data = application.get('website')
        form.redirect_uri.data = application.get('redirect_uri')
    return render_template('profile/applications/edit.html', form=form)


@profile_apps_bp.route('/<client_id>/delete', endpoint='delete')
@login_required
def delete_handler(client_id):
    try:
        message = server.delete_application(client_id, current_user.access_token)
    except APIError as e:
        flash(e.desc, 'error')
    else:
        flash(gettext('You have deleted an application.'), 'success')
    return redirect(url_for('.index'))


@profile_apps_bp.route('/<client_id>/token/delete', endpoint='token_delete')
@login_required
def token_delete_handler(client_id):
    try:
        message = server.delete_token(client_id, current_user.access_token)
    except APIError as e:
        flash(e.desc, 'error')
    return redirect(url_for('.index'))

