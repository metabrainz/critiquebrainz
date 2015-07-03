from itertools import groupby
from flask import Blueprint, render_template
from flask_babel import gettext
from critiquebrainz.data.model.admin_log import AdminLog
from werkzeug.exceptions import NotFound

log_bp = Blueprint('log', __name__)

RESULTS_LIMIT = 20


@log_bp.route('/')
def browse():
    results, count = AdminLog.list()

    if not results:
        raise NotFound(gettext("No logs to display."))

    results = groupby(results, lambda log: log.timestamp.strftime('%d %b, %G'))

    return render_template('log/log.html', results=results)
