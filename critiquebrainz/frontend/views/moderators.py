from flask import Blueprint, render_template
from critiquebrainz.data.model.user import User
from custom_config import ADMINS

moderators_bp = Blueprint('moderators', __name__)


@moderators_bp.route('/moderators')
def page():
    users = User.query.filter(User.display_name.in_(ADMINS)).all()
    return render_template('moderators/moderators.html', users=users)
