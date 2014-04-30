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

# register error handlers
import errors

# register blueprints
from login.views import bp as bp1
app.register_blueprint(bp1, url_prefix='/login')
from oauth.views import bp as bp2
app.register_blueprint(bp2, url_prefix='/oauth')
from profile.review.views import bp as bp3
app.register_blueprint(bp3, url_prefix='/profile/review')
from profile.details.views import bp as bp4
app.register_blueprint(bp4, url_prefix='/profile/details')
from profile.client.views import bp as bp5
app.register_blueprint(bp5, url_prefix='/profile/client')
from review.views import bp as bp6
app.register_blueprint(bp6, url_prefix='/review')
from user.views import bp as bp7
app.register_blueprint(bp7, url_prefix='/user')
from search.views import bp as bp8
app.register_blueprint(bp8, url_prefix='/search')
from album.views import bp as bp9
app.register_blueprint(bp9, url_prefix='/album')
from about.views import bp as bp10
app.register_blueprint(bp10, url_prefix='/about')
