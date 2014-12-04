from flask import render_template
from exceptions import *


def init_error_handlers(app):

    @app.errorhandler(InvalidRequest)
    @app.errorhandler(400)
    def not_found_handler(error):
        return render_template('errors/400.html', error=error), 400

    @app.errorhandler(AccessDenied)
    @app.errorhandler(403)
    def not_found_handler(error):
        return render_template('errors/403.html', error=error), 403

    @app.errorhandler(NotFound)
    @app.errorhandler(404)
    def not_found_handler(error):
        return render_template('errors/404.html', error=error), 404

    @app.errorhandler(500)
    def exception_handler(error):
        return render_template('errors/500.html', error=error), 500

    @app.errorhandler(503)
    def unavailable_handler(error):
        return render_template('errors/503.html', error=error), 503
