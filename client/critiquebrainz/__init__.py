from flask import Flask

_name = "CritiqueBrainz Client"
_version = "0.1"

# app init
app = Flask(__name__)
app.config.from_object('critiquebrainz.config')

# register api
import api

# register musicbrainz api
from musicbrainz import musicbrainz
musicbrainz.init_app(app, _name, _version)

# register login
from login import login_manager
login_manager.init_app(app)

# register uuid converter
from flask.ext.uuid import FlaskUUID
FlaskUUID(app)

# register datetime formatter
from utils import format_datetime
app.jinja_env.filters['datetime'] = format_datetime

# register index
import views

# register blueprints
from login.views import bp as bp1
app.register_blueprint(bp1, url_prefix='/login')
from oauth.views import bp as bp2
app.register_blueprint(bp2, url_prefix='/oauth')
from user.publication.views import bp as bp3
app.register_blueprint(bp3, url_prefix='/user/publication')
