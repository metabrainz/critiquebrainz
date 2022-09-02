import logging
import os
import sys
from time import sleep

from brainzutils.flask import CustomFlask

deploy_env = os.environ.get('DEPLOY_ENV', '')
CONSUL_CONFIG_FILE_RETRY_COUNT = 10
REVIEWS_LIMIT = 5


def create_app(debug=None, config_path=None):
    app = CustomFlask(
        import_name=__name__,
        use_flask_uuid=True,
    )

    # Configuration files
    app.config.from_pyfile(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', '..', 'default_config.py'
    ))

    config_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', '..', 'consul_config.py'
    )
    if deploy_env:
        print("Checking if consul template generated config file exists: {}".format(config_file))
        for _ in range(CONSUL_CONFIG_FILE_RETRY_COUNT):
            if not os.path.exists(config_file):
                sleep(1)

        if not os.path.exists(config_file):
            print("No configuration file generated yet. Retried {} times, exiting.".format(
                CONSUL_CONFIG_FILE_RETRY_COUNT))
            sys.exit(-1)

        print("Loading consul config file {}".format(config_file))
    app.config.from_pyfile(config_file, silent=True)

    app.config.from_pyfile(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', '..', 'custom_config.py'
    ), silent=True)
    if config_path:
        app.config.from_pyfile(config_path)
    if debug is not None:
        app.debug = debug

    # Error handling
    from critiquebrainz.ws.errors import init_error_handlers
    init_error_handlers(app)

    # Sentry
    from brainzutils import sentry
    dsn = sentry_config=app.config.get("LOG_SENTRY")
    if dsn:
        sentry.init_sentry(dsn)

    # CritiqueBrainz Database
    from critiquebrainz import db as critiquebrainz_db
    critiquebrainz_db.init_db_engine(app.config.get("SQLALCHEMY_DATABASE_URI"))

    # BookBrainz Database
    import critiquebrainz.frontend.external.bookbrainz_db as bookbrainz_db 
    bookbrainz_db.init_db_engine(app.config.get("BB_DATABASE_URI"))

    # MusicBrainz Database
    from brainzutils import musicbrainz_db
    musicbrainz_db.init_db_engine(app.config.get("MB_DATABASE_URI"))

    # Redis (cache)
    from brainzutils import cache
    if "REDIS_HOST" in app.config and \
            "REDIS_PORT" in app.config and \
            "REDIS_NAMESPACE" in app.config:
        cache.init(
            host=app.config["REDIS_HOST"],
            port=app.config["REDIS_PORT"],
            namespace=app.config["REDIS_NAMESPACE"],
        )
    else:
        logging.warning("Redis is not defined in config file. Skipping initialization.")

    from critiquebrainz.frontend import babel
    babel.init_app(app, domain='cb_webservice')

    # OAuth
    from critiquebrainz.ws.oauth import oauth
    oauth.init_app(app)

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
    from critiquebrainz.ws.review.bulk import bulk_review_bp
    from critiquebrainz.ws.artist.views import artist_bp
    from critiquebrainz.ws.label.views import label_bp
    from critiquebrainz.ws.event.views import event_bp
    from critiquebrainz.ws.place.views import place_bp
    from critiquebrainz.ws.recording.views import recording_bp
    from critiquebrainz.ws.release_group.views import release_group_bp
    from critiquebrainz.ws.work.views import work_bp
    from critiquebrainz.ws.bb_author.views import author_bp
    from critiquebrainz.ws.bb_edition_group.views import edition_group_bp
    from critiquebrainz.ws.bb_literary_work.views import literary_work_bp
    from critiquebrainz.ws.bb_series.views import series_bp
    app.register_blueprint(oauth_bp, url_prefix="/oauth")
    app.register_blueprint(review_bp, url_prefix="/review")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(bulk_review_bp, url_prefix="/reviews")
    app.register_blueprint(artist_bp, url_prefix="/artist")
    app.register_blueprint(label_bp, url_prefix="/label")
    app.register_blueprint(event_bp, url_prefix="/event")
    app.register_blueprint(place_bp, url_prefix="/place")
    app.register_blueprint(recording_bp, url_prefix="/recording")
    app.register_blueprint(release_group_bp, url_prefix="/release-group")
    app.register_blueprint(work_bp, url_prefix="/work")
    app.register_blueprint(author_bp, url_prefix="/author")
    app.register_blueprint(edition_group_bp, url_prefix="/edition-group")
    app.register_blueprint(literary_work_bp, url_prefix="/literary-work")
    app.register_blueprint(series_bp, url_prefix="/series")

