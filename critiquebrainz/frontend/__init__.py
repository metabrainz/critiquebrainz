import logging
import os
import sys
from time import sleep

import jinja2

from brainzutils.flask import CustomFlask
from flask import send_from_directory

deploy_env = os.environ.get('DEPLOY_ENV', '')
CONSUL_CONFIG_FILE_RETRY_COUNT = 10


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
    if app.debug and app.config['SECRET_KEY']:
        app.init_debug_toolbar()
        app.jinja_options['undefined'] = jinja2.StrictUndefined

    # Error handling
    from critiquebrainz.frontend.error_handlers import init_error_handlers
    init_error_handlers(app)

    # Static files
    from critiquebrainz.frontend import static_manager
    static_manager.read_manifest()

    # Sentry
    from brainzutils import sentry

    dsn = sentry_config=app.config.get("LOG_SENTRY")
    if dsn:
        sentry.init_sentry(dsn)

    # CritiqueBrainz Database
    from critiquebrainz import db as critiquebrainz_db
    critiquebrainz_db.init_db_engine(app.config.get("SQLALCHEMY_DATABASE_URI"))

    add_robots(app)

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
    babel.init_app(app)

    from critiquebrainz.frontend import login
    login.login_manager.init_app(app)
    from critiquebrainz.frontend.login.provider import MusicBrainzAuthentication
    login.mb_auth = MusicBrainzAuthentication(
        name='musicbrainz',
        client_id=app.config['MUSICBRAINZ_CLIENT_ID'],
        client_secret=app.config['MUSICBRAINZ_CLIENT_SECRET'],
        authorize_url="https://musicbrainz.org/oauth2/authorize",
        access_token_url="https://musicbrainz.org/oauth2/token",
        base_url="https://musicbrainz.org/",
    )

    # APIs
    from critiquebrainz.frontend.external import mbspotify
    mbspotify.init(app.config['MBSPOTIFY_BASE_URI'], app.config['MBSPOTIFY_ACCESS_KEY'])
    from critiquebrainz.frontend.external import musicbrainz
    musicbrainz.init(
        app_name=app.config['MUSICBRAINZ_USERAGENT'] or "CritiqueBrainz Custom",
        app_version="1.0",
        hostname=app.config['MUSICBRAINZ_HOSTNAME'] or "musicbrainz.org",
    )

    # Template utilities
    # TODO (code-master5): disabled no-member warnings just as a workaround to deal with failing tests till the
    # issue [https://github.com/PyCQA/pylint/issues/2563] with pylint is resolved
    app.jinja_env.add_extension('jinja2.ext.do')
    from critiquebrainz.utils import reformat_date, reformat_datetime, track_length, track_length_ms, parameterize
    from critiquebrainz.frontend.external.musicbrainz_db.entities import get_entity_by_id
    from critiquebrainz.frontend.external.musicbrainz_db import mbstore, development_get_entity_by_id
    mbstore.init_app(app)
    from critiquebrainz.frontend.forms.utils import get_language_name
    app.jinja_env.filters['date'] = reformat_date
    app.jinja_env.filters['datetime'] = reformat_datetime
    app.jinja_env.filters['track_length'] = track_length
    app.jinja_env.filters['track_length_ms'] = track_length_ms
    app.jinja_env.filters['parameterize'] = parameterize
    if app.config["DEBUG"]:
        app.jinja_env.filters['entity_details'] = development_get_entity_by_id
    else:
        app.jinja_env.filters['entity_details'] = get_entity_by_id
    app.jinja_env.filters['language_name'] = get_language_name
    app.context_processor(lambda: dict(get_static_path=static_manager.get_static_path))

    # Blueprints
    from critiquebrainz.frontend.views.index import frontend_bp
    from critiquebrainz.frontend.views.review import review_bp
    from critiquebrainz.frontend.views.search import search_bp
    from critiquebrainz.frontend.views.artist import artist_bp
    from critiquebrainz.frontend.views.label import label_bp
    from critiquebrainz.frontend.views.release_group import release_group_bp
    from critiquebrainz.frontend.views.release import release_bp
    from critiquebrainz.frontend.views.work import work_bp
    from critiquebrainz.frontend.views.recording import recording_bp
    from critiquebrainz.frontend.views.event import event_bp
    from critiquebrainz.frontend.views.bb_edition_group import edition_group_bp
    from critiquebrainz.frontend.views.mapping import mapping_bp
    from critiquebrainz.frontend.views.user import user_bp
    from critiquebrainz.frontend.views.profile import profile_bp
    from critiquebrainz.frontend.views.place import place_bp
    from critiquebrainz.frontend.views.profile_apps import profile_apps_bp
    from critiquebrainz.frontend.views.login import login_bp
    from critiquebrainz.frontend.views.oauth import oauth_bp
    from critiquebrainz.frontend.views.reports import reports_bp
    from critiquebrainz.frontend.views.moderators import moderators_bp
    from critiquebrainz.frontend.views.log import log_bp
    from critiquebrainz.frontend.views.comment import comment_bp
    from critiquebrainz.frontend.views.rate import rate_bp
    from critiquebrainz.frontend.views.statistics import statistics_bp

    app.register_blueprint(frontend_bp)
    app.register_blueprint(review_bp, url_prefix='/review')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(artist_bp, url_prefix='/artist')
    app.register_blueprint(label_bp, url_prefix='/label')
    app.register_blueprint(release_group_bp, url_prefix='/release-group')
    app.register_blueprint(release_bp, url_prefix='/release')
    app.register_blueprint(work_bp, url_prefix='/work')
    app.register_blueprint(recording_bp, url_prefix='/recording')
    app.register_blueprint(event_bp, url_prefix='/event')
    app.register_blueprint(place_bp, url_prefix='/place')
    app.register_blueprint(edition_group_bp, url_prefix='/edition-group')
    app.register_blueprint(mapping_bp, url_prefix='/mapping')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(profile_apps_bp, url_prefix='/profile/applications')
    app.register_blueprint(login_bp, url_prefix='/login')
    app.register_blueprint(oauth_bp, url_prefix='/oauth')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(log_bp, url_prefix='/log')
    app.register_blueprint(moderators_bp, url_prefix='/moderators')
    app.register_blueprint(comment_bp, url_prefix='/comments')
    app.register_blueprint(rate_bp, url_prefix='/rate')
    app.register_blueprint(statistics_bp, url_prefix='/statistics')

    return app


def add_robots(app):
    @app.route('/robots.txt')
    def robots_txt():  # pylint: disable=unused-variable
        return send_from_directory(app.static_folder, 'robots.txt')
