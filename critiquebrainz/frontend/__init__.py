import os

from flask import Flask
from flask_babel import Locale, get_locale


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
    from critiquebrainz.frontend.error_handlers import init_error_handlers
    init_error_handlers(app)

    # Logging
    from critiquebrainz import loggers
    loggers.init_loggers(app)

    if app.debug:
        # Debug toolbar
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)
        app.config['DEBUG_TB_TEMPLATE_EDITOR_ENABLED'] = True

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

    import critiquebrainz.frontend.babel
    babel.init_app(app)

    import critiquebrainz.frontend.login
    login.login_manager.init_app(app)
    from critiquebrainz.frontend.login.provider import MusicBrainzAuthentication
    login.mb_auth = MusicBrainzAuthentication(
        name='musicbrainz',
        client_id=app.config['MUSICBRAINZ_CLIENT_ID'],
        client_secret=app.config['MUSICBRAINZ_CLIENT_SECRET'],
        authorize_url="https://musicbrainz.org/oauth2/authorize",
        access_token_url="https://musicbrainz.org/oauth2/token",
        base_url="https://musicbrainz.org/")

    # APIs
    from critiquebrainz.frontend.external import mbspotify
    mbspotify.init(app.config['MBSPOTIFY_BASE_URI'], app.config['MBSPOTIFY_ACCESS_KEY'])
    from critiquebrainz.frontend.external import musicbrainz
    musicbrainz.init(app.config['MUSICBRAINZ_USERAGENT'], critiquebrainz.__version__,
                     hostname=app.config['MUSICBRAINZ_HOSTNAME'])

    # Template utilities
    app.jinja_env.add_extension('jinja2.ext.do')
    from critiquebrainz.utils import reformat_date, reformat_datetime, track_length, parameterize
    app.jinja_env.filters['date'] = reformat_date
    app.jinja_env.filters['datetime'] = reformat_datetime
    app.jinja_env.filters['track_length'] = track_length
    app.jinja_env.filters['parameterize'] = parameterize
    app.jinja_env.filters['entity_details'] = musicbrainz.get_entity_by_id
    app.jinja_env.filters['language_name'] = lambda language_code: Locale(language_code).get_language_name(get_locale())

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

    return app
