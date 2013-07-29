#!/usr/bin/python
from flask.ext.script import Manager
from critiquebrainz import app

manager = Manager(app)

if __name__ == '__main__':
    manager.run()
