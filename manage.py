#!/usr/bin/python
from flask.ext.script import Manager

from critiquebrainz import fixtures as _fixtures
from critiquebrainz import app, db

manager = Manager(app)

@manager.command
def tables():
    db.create_tables(app)

@manager.command
def fixtures():
    _fixtures.install(app, *_fixtures.all_data)

if __name__ == '__main__':
    manager.run()

