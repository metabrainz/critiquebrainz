from flask import Flask

app_name = "CritiqueBrainz Client"
app_version = "0.1"

app = Flask(__name__)
app.config.from_object('critiquebrainz.config')

# init apis
import apis

# init login
from login import login_manager
login_manager.init_app(app)

# init uuid converter
from flask.ext.uuid import FlaskUUID
FlaskUUID(app)

# init utils
from utils import format_datetime, track_length
app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['track_length'] = track_length

# init error handlers
import errors

# init index
import views

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
from release_group.views import bp as bp9
app.register_blueprint(bp9, url_prefix='/release-group')
from artist.views import bp as bp10
app.register_blueprint(bp10, url_prefix='/artist')
from about.views import bp as bp11
app.register_blueprint(bp11, url_prefix='/about')
from matching.views import bp as bp12
app.register_blueprint(bp12, url_prefix='/matching')
