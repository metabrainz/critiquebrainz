from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# app init
app = Flask(__name__)
app.config.from_object('config')

# register a converter for uuid
from utils import UUIDConverter
UUIDConverter._register(app)

# database init
import models
db = models.init_app(app)

# register views
import views
