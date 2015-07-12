from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from critiquebrainz.data.model.spam_report import SpamReport
from critiquebrainz.frontend.login import admin_view
from sqlalchemy import desc

reports_bp = Blueprint('reports', __name__)

RESULTS_LIMIT = 20


@reports_bp.route('/')
@login_required
@admin_view
def index():
    count = SpamReport.query.count()
    results = SpamReport.query.order_by(desc(SpamReport.reported_at)).limit(RESULTS_LIMIT)

    return render_template('reports/reports.html', count=count, results=results, limit=RESULTS_LIMIT)


@reports_bp.route('/more')
@login_required
@admin_view
def more():
    page = int(request.args.get('page', default=0))
    offset = page * RESULTS_LIMIT

    count = SpamReport.query.count()
    results = SpamReport.query.order_by(desc(SpamReport.reported_at)).offset(offset).limit(RESULTS_LIMIT)

    template = render_template('reports/reports_results.html', results=results)
    return jsonify(results=template, more=(count-offset-RESULTS_LIMIT) > 0)
