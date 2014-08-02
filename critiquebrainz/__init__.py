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
        loggers.init_loggers(app)

    from flask.ext.uuid import FlaskUUID
    FlaskUUID(app)

    from data import db
    db.init_app(app)

    with app.app_context():
        import frontend.apis
        import frontend.babel
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
    import frontend
    frontend.register_blueprints(app)

    # Web service blueprints
    import ws
    ws.register_blueprints(app)

    return app
