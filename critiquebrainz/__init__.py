from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import config

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

# register uuid converter
from utils import UUIDConverter
UUIDConverter._register(app)

# register blueprints
from login.views import login
app.register_blueprint(login)
from ui.views import ui
app.register_blueprint(ui)
from oauth.views import oauth as oauth_blueprint
app.register_blueprint(oauth_blueprint)
import api
api.register_blueprints(app, '/ws/1')