from flask import Blueprint, render_template, redirect, url_for
from flask_babel import gettext
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound

import critiquebrainz.db.oauth_client as db_oauth_client
import critiquebrainz.db.exceptions as db_exceptions
import critiquebrainz.db.oauth_token as db_oauth_token
from critiquebrainz.frontend.forms.profile_apps import ApplicationForm
from critiquebrainz.frontend import flash
import critiquebrainz.db.users as db_users

profile_apps_bp = Blueprint('profile_applications', __name__)


@profile_apps_bp.route('/')
@login_required
def index():
    return render_template('profile/applications/index.html',
                           applications=db_users.clients(current_user.id),
                           tokens=db_users.tokens(current_user.id))


@profile_apps_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create application."""
    form = ApplicationForm()
    if form.validate_on_submit():
        db_oauth_client.create(
            user_id=current_user.id,
            name=form.name.data,
            desc=form.desc.data,
            website=form.website.data,
            redirect_uri=form.redirect_uri.data,
        )
        flash.success(gettext('You have created an application!'))
        return redirect(url_for('.index'))
    return render_template('profile/applications/create.html', form=form)


@profile_apps_bp.route('/<client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(client_id):
    try:
        application = db_oauth_client.get_client(client_id)
    except db_exceptions.NoDataFoundException:
        raise NotFound()
    if str(application["user_id"]) != current_user.id:
        raise NotFound()
    form = ApplicationForm()
    if form.validate_on_submit():
        db_oauth_client.update(
            client_id=application["client_id"],
            name=form.name.data,
            desc=form.desc.data,
            website=form.website.data,
            redirect_uri=form.redirect_uri.data,
        )
        flash.success(gettext("You have updated an application!"))
        return redirect(url_for('.index'))
    else:
        form.name.data = application["name"]
        form.desc.data = application["desc"]
        form.website.data = application["website"]
        form.redirect_uri.data = application["redirect_uri"]
    return render_template('profile/applications/edit.html', form=form)


@profile_apps_bp.route('/<client_id>/delete')
@login_required
def delete(client_id):
    try:
        application = db_oauth_client.get_client(client_id)
    except db_exceptions.NoDataFoundException:
        raise NotFound()
    if str(application["user_id"]) != current_user.id:
        raise NotFound()
    db_oauth_client.delete(application["client_id"])

    flash.success(gettext('You have deleted an application.'))
    return redirect(url_for('.index'))


@profile_apps_bp.route('/<client_id>/token/delete')
@login_required
def token_delete(client_id):
    db_oauth_token.delete(client_id=client_id, user_id=current_user.id)
    return redirect(url_for('.index'))
