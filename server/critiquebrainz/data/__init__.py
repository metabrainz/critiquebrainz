from sqlalchemy import create_engine
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_tables(app):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    db.metadata.create_all(engine)
    return engine
