from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_babel import gettext
from critiquebrainz.frontend.profile.forms import ProfileEditForm


profile_bp = Blueprint('profile_details', __name__)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = ProfileEditForm()
    if form.validate_on_submit():
        current_user.update(display_name=form.display_name.data,
                            email=form.email.data,
                            show_gravatar=form.show_gravatar.data)
        flash(gettext("Profile updated."), 'success')
        return redirect(url_for('user.reviews', user_id=current_user.id))
    else:
        form.display_name.data = current_user.display_name
        form.email.data = current_user.email
        form.show_gravatar.data = current_user.show_gravatar
    return render_template('profile/edit.html', form=form)


@profile_bp.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    if request.method == 'POST':
        current_user.delete()
        return redirect(url_for('frontend.index'))
    return render_template('profile/delete.html')

