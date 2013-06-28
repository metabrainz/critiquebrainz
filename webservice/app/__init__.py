from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

from utils.converters import FlaskUUID
FlaskUUID(app)

db = SQLAlchemy(app)

import models
import views
