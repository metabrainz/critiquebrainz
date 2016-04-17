from flask import Flask
import os


def create_app(debug=None):
    app = Flask(__name__)

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

    # Logging
    from critiquebrainz import loggers
    loggers.init_loggers(app)

    from flask_uuid import FlaskUUID
    FlaskUUID(app)

    from critiquebrainz.data import db
    db.init_app(app)

    # Memcached
    if 'MEMCACHED_SERVERS' in app.config:
        from critiquebrainz import cache
        cache.init(app.config['MEMCACHED_SERVERS'],
                   app.config['MEMCACHED_NAMESPACE'],
                   debug=1 if app.debug else 0)

    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

    _register_blueprints(app)

    return app


def create_app_sphinx():
    app = Flask(__name__)
    _register_blueprints(app)
    return app


def _register_blueprints(app):
    from critiquebrainz.ws.oauth.views import oauth_bp
    from critiquebrainz.ws.review.views import review_bp
    from critiquebrainz.ws.user.views import user_bp
    app.register_blueprint(oauth_bp, url_prefix='/oauth')
    app.register_blueprint(review_bp, url_prefix='/review')
    app.register_blueprint(user_bp, url_prefix='/user')
