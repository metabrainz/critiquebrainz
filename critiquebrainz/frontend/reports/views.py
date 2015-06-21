from flask import Blueprint, render_template
from flask_login import login_required, current_user
from werkzeug.exceptions import Unauthorized
from critiquebrainz.data.model.spam_report import SpamReport

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/')
@login_required
def index():
    if not current_user.is_admin():
        raise Unauthorized('You must be an administrator to view this page.')
    reports, count = SpamReport.list()
    return render_template('reports/reports.html', reports=reports)

