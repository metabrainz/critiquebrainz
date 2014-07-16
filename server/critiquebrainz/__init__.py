from flask import Flask
import critiquebrainz.default_config

import os
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if not on_rtd:
    import config
else:
    import shutil
    path = os.path.dirname(__file__)
    shutil.copyfile(path+'/config.py.example', path+'/config.py')

_name = "CritiqueBrainz Server"
__version__ = "0.1"

# SNI support for Python 2
# See http://urllib3.readthedocs.org/en/latest/contrib.html#module-urllib3.contrib.pyopenssl
try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass


def create_app():
    app = Flask(__name__)
    app.config.from_object(critiquebrainz.default_config)
    app.config.from_object('critiquebrainz.config')

    from db import db as _db
    _db.init_app(app)

    # oauth init
    from oauth import oauth
    oauth.init_app(app)

    # register uuid converter
    from flask.ext.uuid import FlaskUUID
    FlaskUUID(app)

    # register error handlers
    import errors
    errors.init_error_handlers(app)

    # register loggers
    import loggers
    if app.debug is False:
        loggers.init_app(app)

    import login
    login.init_oauth_providers(app)

    # register blueprints
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


app = create_app()
