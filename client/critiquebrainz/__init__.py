from flask import Flask
import critiquebrainz.default_config

app_name = "CritiqueBrainz Client"
app_version = "0.1"

app = Flask(__name__)
app.config.from_object(critiquebrainz.default_config)
app.config.from_object('critiquebrainz.config')

# SNI support for Python 2
# See http://urllib3.readthedocs.org/en/latest/contrib.html#module-urllib3.contrib.pyopenssl
try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass

# init apis
import apis

with app.app_context():
    # init babel
    import babel

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

# init loggers
if app.debug is False:
    import loggers
    loggers.init_app(app)

# init index
import views

# register blueprints
from login.views import bp as bp1
app.register_blueprint(bp1, url_prefix='/login')
from oauth.views import bp as bp2
app.register_blueprint(bp2, url_prefix='/oauth')
from critiquebrainz.profile.views import bp as bp4
app.register_blueprint(bp4, url_prefix='/profile')
from profile.applications.views import bp as bp5
app.register_blueprint(bp5, url_prefix='/profile/applications')
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
from matching.views import bp as bp11
app.register_blueprint(bp11, url_prefix='/matching')
