from flask import Blueprint, render_template, request, redirect, url_for
from flask_babel import gettext
from flask_login import login_required, current_user

import critiquebrainz.db.users as db_users
from critiquebrainz.frontend import flash
from critiquebrainz.frontend.forms.profile import ProfileEditForm

profile_bp = Blueprint('profile_details', __name__)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = ProfileEditForm()
    if form.validate_on_submit():
        db_users.update(current_user.id, user_new_info={
            "display_name": form.display_name.data,
            "email": form.email.data,
            "license_choice": form.license_choice.data,
        })
        flash.success(gettext("Profile updated."))
        return redirect(url_for('user.reviews', user_ref= current_user.musicbrainz_username if current_user.musicbrainz_username else current_user.id))

    form.display_name.data = current_user.display_name
    form.email.data = current_user.email
    form.license_choice.data = current_user.license_choice
    return render_template('profile/edit.html', form=form)


@profile_bp.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    if request.method == 'POST':
        db_users.delete(current_user.id)
        return redirect(url_for('frontend.index'))
    return render_template('profile/delete.html')
