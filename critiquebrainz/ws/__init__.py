from flask import Flask


def create_app():
    app = Flask(__name__)

    # Configuration files
    import critiquebrainz.default_config
    app.config.from_object(critiquebrainz.default_config)
    app.config.from_object('critiquebrainz.config')

    # Error handling
    import errors
    errors.init_error_handlers(app)

    # Logging
    if app.debug is False:
        from critiquebrainz import loggers
        loggers.init_loggers(app)

    from flask.ext.uuid import FlaskUUID
    FlaskUUID(app)

    from critiquebrainz.data import db
    db.init_app(app)

    from critiquebrainz.cache import cache
    cache.set_servers(app.config['MEMCACHED_SERVERS'])

    # Blueprints
    from oauth.views import oauth_bp
    from review.views import review_bp
    from user.views import user_bp

    app.register_blueprint(oauth_bp, url_prefix='/oauth')
    app.register_blueprint(review_bp, url_prefix='/review')
    app.register_blueprint(user_bp, url_prefix='/user')

    return app
