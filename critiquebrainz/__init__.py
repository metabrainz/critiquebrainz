from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import config

_name = "CritiqueBrainz"
_version = "0.1"

# app init
app = Flask(__name__)
app.config.from_object('critiquebrainz.config')

# db init
import db
db.init_app(app)

# login init
import login
login.init_app(app)

# oauth init
import oauth
oauth.init_app(app)

# musicbrainz init
import musicbrainz
musicbrainz.init_app(_name, _version)

# register uuid converter
from utils import UUIDConverter
UUIDConverter._register(app)

# register blueprints
from login.views import login
app.register_blueprint(login)
from oauth.views import oauth as oauth_blueprint
app.register_blueprint(oauth_blueprint)
import api
api.register_blueprints(app, '/ws/1')
import user
user.register_blueprints(app, '/user')

@app.route('/', endpoint='index')
def index_handler():
    return 'Temporary index.'
