from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import models

app = Flask(__name__)
app.config.from_object('config')
db = models.init_app(app)

from utils.converters import FlaskUUID
FlaskUUID(app)

import views
