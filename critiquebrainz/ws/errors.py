# pylint: disable=unused-variable
from flask import jsonify
from critiquebrainz.ws import exceptions as ws_exceptions


def init_error_handlers(app):

    @app.errorhandler(ws_exceptions.WebServiceError)
    def base_error_handler(error):
        return jsonify(error=error.code, description=error.desc), error.status

    @app.errorhandler(ws_exceptions.ParserError)
    def parser_error_handler(error):
        return base_error_handler(ws_exceptions.InvalidRequest('Parameter `%s`: %s' % (error.key, error.desc)))

    @app.errorhandler(401)
    def not_authorized_handler():
        return base_error_handler(ws_exceptions.NotAuthorized())

    @app.errorhandler(403)
    def access_denied_handler():
        return base_error_handler(ws_exceptions.AccessDenied())

    @app.errorhandler(404)
    def not_found_handler():
        return base_error_handler(ws_exceptions.NotFound())

    @app.errorhandler(500)
    def exception_handler():
        return base_error_handler(ws_exceptions.ServerError())
