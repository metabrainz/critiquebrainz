from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from flask_babel import gettext
from werkzeug.exceptions import Unauthorized
from critiquebrainz.data.model.spam_report import SpamReport
from sqlalchemy import desc

reports_bp = Blueprint('reports', __name__)

RESULTS_LIMIT = 20


@reports_bp.route('/')
@login_required
def index():
    if not current_user.is_admin():
        raise Unauthorized(gettext('You must be an administrator to view this page.'))

    count = SpamReport.query.count()
    results = SpamReport.query.order_by(desc(SpamReport.reported_at)).limit(RESULTS_LIMIT)

    return render_template('reports/reports.html', count=count, results=results, limit=RESULTS_LIMIT)


@reports_bp.route('/more')
def more():
    if not current_user.is_admin():
        raise Unauthorized(gettext('You must be an administrator to view this page.'))

    page = int(request.args.get('page', default=0))
    offset = page * RESULTS_LIMIT

    count = SpamReport.query.count()
    results = SpamReport.query.order_by(desc(SpamReport.reported_at)).offset(offset).limit(RESULTS_LIMIT)

    template = render_template('reports/reports_results.html', results=results)
    return jsonify(results=template, more=(count-offset-RESULTS_LIMIT) > 0)
