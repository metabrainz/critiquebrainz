from flask import jsonify

from critiquebrainz.exceptions import *


def init_error_handlers(app):
    @app.errorhandler(BaseError)
    def base_error_handler(error):
        return jsonify(error=error.code, description=error.desc), error.status


    @app.errorhandler(ParserError)
    def parser_error_handler(error):
        return base_error_handler(InvalidRequest('Parameter `%s`: %s' % (error.key, error.desc)))

    @app.errorhandler(401)
    def oauth_error_handler(error):
        return base_error_handler(NotAuthorized())


    @app.errorhandler(403)
    def oauth_error_handler(error):
        return base_error_handler(AccessDenied())


    @app.errorhandler(404)
    def not_found_handler(error):
        return base_error_handler(NotFound())


    @app.errorhandler(500)
    def exception_handler(error):
        return base_error_handler(ServerError())
