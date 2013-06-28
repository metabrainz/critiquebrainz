from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

# app init
app = Flask(__name__)
app.config.from_object('config')

# register url converters
from utils.converters import FlaskUUID
FlaskUUID(app)

# db init
db = SQLAlchemy(app)

# import modules
import users
import reviews
import reports
import votes


