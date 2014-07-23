from flask import Flask

__version__ = "0.1"


# Config file creation for ReadTheDocs
# See http://read-the-docs.readthedocs.org/en/latest/faq.html#how-do-i-change-behavior-for-read-the-docs
import os
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    import shutil
    path = os.path.dirname(__file__)
    shutil.copyfile(path+'/config.py.example', path+'/config.py')

# SNI support for Python 2
# See http://urllib3.readthedocs.org/en/latest/contrib.html#module-urllib3.contrib.pyopenssl
try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass


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

    from oauth import oauth
    oauth.init_app(app)

    import login
    login.init_oauth_providers(app)

    # Blueprints
    from oauth.views import oauth_bp
    from login.views import login_bp
    from review.views import review_bp
    from user.views import user_bp
    from app.views import app_bp

    app.register_blueprint(oauth_bp, url_prefix='/oauth')
    app.register_blueprint(login_bp, url_prefix='/login')
    app.register_blueprint(review_bp, url_prefix='/review')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(app_bp, url_prefix='/application')

    return app
