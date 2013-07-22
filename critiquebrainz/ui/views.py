from flask import Blueprint, render_template
from flask.ext.login import current_user

ui = Blueprint('ui', __name__, url_prefix='/')

@ui.route('/', endpoint='index')
def ui_index_handler():
	return render_template('base.html')
