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
        loggers.add_all_loggers(app)

    from flask.ext.uuid import FlaskUUID
    FlaskUUID(app)

    from critiquebrainz.data import db
    db.init_app(app)

    import babel
    babel.init_app(app)

    import login
    login.login_manager.init_app(app)
    from login.provider import MusicBrainzAuthentication
    login.mb_auth = MusicBrainzAuthentication(
        name='musicbrainz',
        client_id=app.config['MUSICBRAINZ_CLIENT_ID'],
        client_secret=app.config['MUSICBRAINZ_CLIENT_SECRET'],
        authorize_url="https://musicbrainz.org/oauth2/authorize",
        access_token_url="https://musicbrainz.org/oauth2/token",
        base_url="https://musicbrainz.org/")

    from apis import mbspotify
    mbspotify.init(app.config['MBSPOTIFY_BASE_URI'], app.config['MBSPOTIFY_ACCESS_KEY'])

    # Template utilities
    app.jinja_env.add_extension('jinja2.ext.do')
    from critiquebrainz.utils import reformat_date, reformat_datetime, track_length
    app.jinja_env.filters['date'] = reformat_date
    app.jinja_env.filters['datetime'] = reformat_datetime
    app.jinja_env.filters['track_length'] = track_length
    from apis import musicbrainz
    app.jinja_env.filters['release_group_details'] = musicbrainz.release_group_details

    # Blueprints
    from views import frontend_bp
    from review.views import review_bp
    from search.views import search_bp
    from artist.views import artist_bp
    from release_group.views import release_group_bp
    from matching.views import matching_bp
    from user.views import user_bp
    from profile.views import profile_bp
    from profile.applications.views import profile_apps_bp
    from login.views import login_bp
    from oauth.views import oauth_bp

    app.register_blueprint(frontend_bp)
    app.register_blueprint(review_bp, url_prefix='/review')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(artist_bp, url_prefix='/artist')
    app.register_blueprint(release_group_bp, url_prefix='/release-group')
    app.register_blueprint(matching_bp, url_prefix='/matching')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(profile_apps_bp, url_prefix='/profile/applications')
    app.register_blueprint(login_bp, url_prefix='/login')
    app.register_blueprint(oauth_bp, url_prefix='/oauth')

    return app
