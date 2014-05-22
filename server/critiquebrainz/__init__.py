from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import config

_name = "CritiqueBrainz Server"
__version__ = "0.1"

# app init
app = Flask(__name__)
app.config.from_object('critiquebrainz.config')

# db init
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

# register loggers
import loggers
if app.debug is False:
    loggers.init_app(app)

# register blueprints
from oauth.views import bp as bp1
app.register_blueprint(bp1, url_prefix='/oauth')
from login.views import bp as bp2
app.register_blueprint(bp2, url_prefix='/login')
from review.views import bp as bp3
app.register_blueprint(bp3, url_prefix='/review')
from user.views import bp as bp4
app.register_blueprint(bp4, url_prefix='/user')
from client.views import bp as bp5
app.register_blueprint(bp5, url_prefix='/client')
