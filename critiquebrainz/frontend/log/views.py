from itertools import groupby
from flask import Blueprint, render_template, flash, request, jsonify
from flask_babel import gettext
from critiquebrainz.data.model.moderation_log import ModerationLog

log_bp = Blueprint('log', __name__)

RESULTS_LIMIT = 20


@log_bp.route('/')
def browse():
    results, count = ModerationLog.list(limit=RESULTS_LIMIT)

    if not results:
        flash(gettext("No logs to display."), "warning")

    results = groupby(results, lambda log: log.timestamp.strftime('%d %b, %G'))

    return render_template('log/log.html', count=count, results=results, limit=RESULTS_LIMIT)


@log_bp.route('/more')
def more():
    page = int(request.args.get('page', default=0))
    offset = page * RESULTS_LIMIT

    results, count = ModerationLog.list(offset=offset, limit=RESULTS_LIMIT)
    results = groupby(results, lambda log: log.timestamp.strftime('%d %b, %G'))

    template = render_template('log/log_results.html', results=results)
    return jsonify(results=template, more=(count-offset-RESULTS_LIMIT) > 0)
