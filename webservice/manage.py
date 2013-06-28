from flask.ext.script import Manager

from app import fixtures as _fixtures
from app import app, models

manager = Manager(app)

@manager.command
def tables():
    models.create_tables(app)

@manager.command
def fixtures():
    _fixtures.install(app, *_fixtures.all_data)

if __name__ == '__main__':
    manager.run()

