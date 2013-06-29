from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

import models
db = models.init_app(app)

from .utils.converters import FlaskUUID
FlaskUUID(app)

import views
views.register_views(app)
