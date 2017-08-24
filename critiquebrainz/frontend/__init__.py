import logging
import os
from brainzutils.flask import CustomFlask
from flask import send_from_directory


def create_app(debug=None, config_path=None):
    app = CustomFlask(
        import_name=__name__,
        use_flask_uuid=True,
        use_debug_toolbar=True,
    )

    # Configuration files
    app.config.from_pyfile(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', '..', 'default_config.py'
    ))
    app.config.from_pyfile(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', '..', 'consul_config.py'
    ), silent=True)
    app.config.from_pyfile(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..', '..', 'custom_config.py'
    ), silent=True)
    if config_path:
        app.config.from_pyfile(config_path)
    if debug is not None:
        app.debug = debug

    # Error handling
    from critiquebrainz.frontend.error_handlers import init_error_handlers
    init_error_handlers(app)

    # Static files
    from critiquebrainz.frontend import static_manager
    static_manager.read_manifest()

    app.init_loggers(
        file_config=app.config.get("LOG_FILE"),
        email_config=app.config.get("LOG_EMAIL"),
        sentry_config=app.config.get("LOG_SENTRY"),
    )

    # Database
    from critiquebrainz.db import init_db_engine
    init_db_engine(app.config.get("SQLALCHEMY_DATABASE_URI"))

    add_robots(app)

    # MusicBrainz Database
    from critiquebrainz.frontend.external import musicbrainz_db
    musicbrainz_db.init_db_engine(app.config.get('MB_DATABASE_URI'))

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
    app.jinja_env.add_extension('jinja2.ext.do')
    from critiquebrainz.utils import reformat_date, reformat_datetime, track_length, parameterize
    from critiquebrainz.frontend.external.musicbrainz_db.entities import get_entity_by_id
    app.jinja_env.filters['date'] = reformat_date
    app.jinja_env.filters['datetime'] = reformat_datetime
    app.jinja_env.filters['track_length'] = track_length
    app.jinja_env.filters['parameterize'] = parameterize
    app.jinja_env.filters['entity_details'] = get_entity_by_id
    from flask_babel import Locale, get_locale
    app.jinja_env.filters['language_name'] = lambda language_code: Locale(language_code).get_language_name(get_locale())
    app.context_processor(lambda: dict(get_static_path=static_manager.get_static_path))

    # Blueprints
    from critiquebrainz.frontend.views.index import frontend_bp
    from critiquebrainz.frontend.views.review import review_bp
    from critiquebrainz.frontend.views.search import search_bp
    from critiquebrainz.frontend.views.artist import artist_bp
    from critiquebrainz.frontend.views.release_group import release_group_bp
    from critiquebrainz.frontend.views.release import release_bp
    from critiquebrainz.frontend.views.event import event_bp
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

    app.register_blueprint(frontend_bp)
    app.register_blueprint(review_bp, url_prefix='/review')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(artist_bp, url_prefix='/artist')
    app.register_blueprint(release_group_bp, url_prefix='/release-group')
    app.register_blueprint(release_bp, url_prefix='/release')
    app.register_blueprint(event_bp, url_prefix='/event')
    app.register_blueprint(place_bp, url_prefix='/place')
    app.register_blueprint(mapping_bp, url_prefix='/mapping')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(profile_apps_bp, url_prefix='/profile/applications')
    app.register_blueprint(login_bp, url_prefix='/login')
    app.register_blueprint(oauth_bp, url_prefix='/oauth')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(log_bp, url_prefix='/log')
    app.register_blueprint(moderators_bp, url_prefix='/moderators')

    return app


def add_robots(app):

    @app.route('/robots.txt')
    def robots_txt():  # pylint: disable=unused-variable
        return send_from_directory(app.static_folder, 'robots.txt')
