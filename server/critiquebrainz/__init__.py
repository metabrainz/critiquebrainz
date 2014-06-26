from flask import Flask

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


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object)

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


app = create_app('critiquebrainz.config')
