from flask import Blueprint, render_template, flash, redirect, url_for, abort
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext

from critiquebrainz.data.model.oauth import OAuthClient, OAuthToken
from critiquebrainz.frontend.forms.profile.client import ClientForm

profile_apps_bp = Blueprint('profile_applications', __name__)


@profile_apps_bp.route('/', endpoint='index')
@login_required
def index_handler():
    return render_template('profile/applications/index.html',
                           applications=[c.to_dict() for c in current_user.clients],
                           tokens=[t.to_dict() for t in current_user.tokens])


@profile_apps_bp.route('/create', endpoint='create', methods=['GET', 'POST'])
@login_required
def create_handler():
    """Create application."""
    form = ClientForm()
    if form.validate_on_submit():
        OAuthClient.generate(user=current_user, name=form.name.data,
                             desc=form.desc.data, website=form.website.data,
                             redirect_uri=form.redirect_uri.data)
        flash(gettext('You have created an application!'), 'success')
        return redirect(url_for('.index'))
    return render_template('profile/applications/create.html', form=form)


@profile_apps_bp.route('/<client_id>/edit', endpoint='edit', methods=['GET', 'POST'])
@login_required
def edit_handler(client_id):
    application = OAuthClient.query.get_or_404(client_id)
    if application.user != current_user:
        abort(403)
    form = ClientForm()
    if form.validate_on_submit():
        application.update(name=form.name.data, desc=form.desc.data,
                           website=form.website.data, redirect_uri=form.redirect_uri.data)
        flash(gettext("You have updated an application!"), 'success')
        return redirect(url_for('.index'))
    else:
        form.name.data = application.name
        form.desc.data = application.desc
        form.website.data = application.website
        form.redirect_uri.data = application.redirect_uri
    return render_template('profile/applications/edit.html', form=form)


@profile_apps_bp.route('/<client_id>/delete', endpoint='delete')
@login_required
def delete_handler(client_id):
    client = OAuthClient.query.get_or_404(client_id)
    if client.user != current_user:
        abort(403)
    client.delete()

    flash(gettext('You have deleted an application.'), 'success')
    return redirect(url_for('.index'))


@profile_apps_bp.route('/<client_id>/token/delete', endpoint='token_delete')
@login_required
def token_delete_handler(client_id):
    OAuthToken.purge_tokens(client_id=client_id, user_id=current_user.id)
    return redirect(url_for('.index'))
