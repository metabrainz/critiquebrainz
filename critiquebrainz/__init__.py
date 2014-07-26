from flask import Flask

__version__ = '0.1'


# SNI support for Python 2
# See http://urllib3.readthedocs.org/en/latest/contrib.html#module-urllib3.contrib.pyopenssl
try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass

# Config file creation for ReadTheDocs
# See http://read-the-docs.readthedocs.org/en/latest/faq.html#how-do-i-change-behavior-for-read-the-docs
import os
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    import shutil
    path = os.path.dirname(__file__)
    shutil.copyfile(path+'/config.py.example', path+'/config.py')


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
        import loggers
        loggers.init_app(app)

    from flask.ext.uuid import FlaskUUID
    FlaskUUID(app)

    from data import db
    db.init_app(app)

    with app.app_context():
        import apis
        import babel
        import frontend.login

    from ws.oauth import oauth
    oauth.init_app(app)

    from frontend.login import login_manager
    login_manager.init_app(app)

    # Template utilities
    app.jinja_env.add_extension('jinja2.ext.do')
    from utils import reformat_date, reformat_datetime, track_length
    app.jinja_env.filters['date'] = reformat_date
    app.jinja_env.filters['datetime'] = reformat_datetime
    app.jinja_env.filters['track_length'] = track_length

    # Frontend blueprints
    from frontend.views import frontend_bp
    from frontend.review.views import review_bp
    from frontend.search.views import search_bp
    from frontend.artist.views import artist_bp
    from frontend.release_group.views import release_group_bp
    from frontend.matching.views import matching_bp
    from frontend.user.views import user_bp
    from frontend.profile.views import profile_bp
    from frontend.profile.applications.views import profile_apps_bp
    from frontend.login.views import login_bp

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

    # Web service blueprints
    from ws.oauth.views import oauth_bp
    from ws.review.views import review_bp
    from ws.user.views import user_bp

    app.register_blueprint(oauth_bp, url_prefix='/ws/1/oauth')
    app.register_blueprint(review_bp, url_prefix='/ws/1/review')
    app.register_blueprint(user_bp, url_prefix='/ws/1/user')

    return app
