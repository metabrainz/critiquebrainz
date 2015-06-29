from itertools import groupby
from flask import Blueprint, render_template
from critiquebrainz.data.model.admin_log import AdminLog

log_bp = Blueprint('log', __name__)

RESULTS_LIMIT = 20


@log_bp.route('/')
def browse():
    results, count = AdminLog.list()

    results = groupby(results, lambda log: log.timestamp.strftime('%d %b, %G'))

    return render_template('log/log.html', results=results)
