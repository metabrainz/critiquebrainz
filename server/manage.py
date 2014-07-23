from critiquebrainz import app, db
﻿from flask.ext.script import Manager
from critiquebrainz.data.manage import data_manager

manager = Manager(app)

manager.add_command('data', data_manager)

if __name__ == '__main__':
    manager.run()
