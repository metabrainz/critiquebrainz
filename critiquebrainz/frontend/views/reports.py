from flask import Blueprint, render_template, flash, url_for, redirect, request, jsonify
from flask_login import login_required
from flask_babel import gettext
from werkzeug.exceptions import NotFound
import critiquebrainz.db.spam_report as db_spam_report
from critiquebrainz.frontend.login import admin_view

reports_bp = Blueprint('reports', __name__)

RESULTS_LIMIT = 20


@reports_bp.route('/')
@login_required
@admin_view
def index():
    results, count = db_spam_report.list_reports(limit=RESULTS_LIMIT, inc_archived=False)
    return render_template('reports/reports.html', count=count, results=results, limit=RESULTS_LIMIT)


@reports_bp.route('/more')
@login_required
@admin_view
def more():
    page = int(request.args.get('page', default=0))
    offset = page * RESULTS_LIMIT
    results, count = db_spam_report.list_reports(offset=offset, limit=RESULTS_LIMIT, inc_archived=False)
    template = render_template('reports/reports_results.html', results=results)
    return jsonify(results=template, more=(count - offset - RESULTS_LIMIT) > 0)


@reports_bp.route('/<uuid:user_id>/<int:revision_id>/archive')
@login_required
@admin_view
def archive(user_id, revision_id):
    report = db_spam_report.get(user_id, revision_id)
    if not report:
        raise NotFound("Can't find the specified report.")

    db_spam_report.archive(user_id, revision_id)
    flash(gettext("Report has been archived."), 'success')
    return redirect(url_for('.index'))
