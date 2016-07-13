from brainzutils.flask import CustomFlask
import os


def create_app(debug=None):
    app = CustomFlask(
        import_name=__name__,
        use_flask_uuid=True,
    )

    # Configuration files
    import critiquebrainz.default_config
    app.config.from_object(critiquebrainz.default_config)
    app.config.from_pyfile(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "..", "config.py"
    ), silent=True)
    if debug is not None:
        app.debug = debug

    # Error handling
    from critiquebrainz.ws.errors import init_error_handlers
    init_error_handlers(app)

    app.init_loggers(
        file_config=app.config.get("LOG_FILE"),
        email_config=app.config.get("LOG_EMAIL"),
        sentry_config=app.config.get("LOG_SENTRY"),
    )

    from critiquebrainz.data import db
    db.init_app(app)

    # Redis (cache)
    from brainzutils import cache
    cache.init(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        namespace=app.config["REDIS_NAMESPACE"],
    )

    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

    _register_blueprints(app)

    return app


def create_app_sphinx():
    app = CustomFlask(__name__)
    _register_blueprints(app)
    return app


def _register_blueprints(app):
    from critiquebrainz.ws.oauth.views import oauth_bp
    from critiquebrainz.ws.review.views import review_bp
    from critiquebrainz.ws.user.views import user_bp
    app.register_blueprint(oauth_bp, url_prefix="/oauth")
    app.register_blueprint(review_bp, url_prefix="/review")
    app.register_blueprint(user_bp, url_prefix="/user")
