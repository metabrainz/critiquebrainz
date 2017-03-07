from flask import Blueprint, render_template, redirect, url_for
from flask_babel import gettext
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound

from critiquebrainz.data.model.oauth_client import OAuthClient
from critiquebrainz.data.model.oauth_token import OAuthToken
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
        OAuthClient.create(user=current_user, name=form.name.data,
                           desc=form.desc.data, website=form.website.data,
                           redirect_uri=form.redirect_uri.data)
        flash.success(gettext('You have created an application!'))
        return redirect(url_for('.index'))
    return render_template('profile/applications/create.html', form=form)


@profile_apps_bp.route('/<client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(client_id):
    application = OAuthClient.query.get_or_404(client_id)
    if application.user != current_user:
        raise NotFound()
    form = ApplicationForm()
    if form.validate_on_submit():
        application.update(name=form.name.data, desc=form.desc.data,
                           website=form.website.data, redirect_uri=form.redirect_uri.data)
        flash.success(gettext("You have updated an application!"))
        return redirect(url_for('.index'))
    else:
        form.name.data = application.name
        form.desc.data = application.desc
        form.website.data = application.website
        form.redirect_uri.data = application.redirect_uri
    return render_template('profile/applications/edit.html', form=form)


@profile_apps_bp.route('/<client_id>/delete')
@login_required
def delete(client_id):
    client = OAuthClient.query.get_or_404(client_id)
    if client.user != current_user:
        raise NotFound()
    client.delete()

    flash.success(gettext('You have deleted an application.'))
    return redirect(url_for('.index'))


@profile_apps_bp.route('/<client_id>/token/delete')
@login_required
def token_delete(client_id):
    OAuthToken.purge_tokens(client_id=client_id, user_id=current_user.id)
    return redirect(url_for('.index'))
