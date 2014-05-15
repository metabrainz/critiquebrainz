from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import login_required, current_user, logout_user
from critiquebrainz.apis import server
from critiquebrainz.exceptions import APIError
from critiquebrainz.forms.profile.details import EditForm

bp = Blueprint('profile_details', __name__)


@bp.route('/', endpoint='index')
@login_required
def index_handler():
    return render_template('profile/details/index.html')


@bp.route('/edit', methods=['GET', 'POST'], endpoint='edit')
@login_required
def edit_handler():
    form = EditForm()
    if form.validate_on_submit():
        try:
            message = server.update_profile(current_user.access_token,
                                         display_name=form.display_name.data,
                                         email=form.email.data,
                                         show_gravatar=form.show_gravatar.data)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            flash(u'Profile updated', 'success')
        return redirect(url_for('.index'))
    else:
        form.display_name.data = current_user.me.get('display_name')
        form.email.data = current_user.me.get('email')
        form.show_gravatar.data = current_user.me.get('show_gravatar')
    return render_template('profile/details/edit.html', form=form)


@bp.route('/delete', methods=['GET', 'POST'], endpoint='delete')
@login_required
def delete_handler():
    if request.method == 'POST':
        try:
            message = server.delete_profile(current_user.access_token)
        except APIError as e:
            flash(e.desc, 'error')
        else:
            logout_user()
        return redirect(url_for('index'))
    return render_template('profile/details/delete.html')

