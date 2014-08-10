from flask.ext.script import Manager
from critiquebrainz.frontend import create_app
from critiquebrainz.data.manage import data_manager

manager = Manager(create_app)

manager.add_command('data', data_manager)

if __name__ == '__main__':
    manager.run()
