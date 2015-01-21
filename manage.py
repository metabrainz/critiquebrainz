from flask_script import Manager
from flask import current_app
from critiquebrainz.frontend import create_app
from critiquebrainz.data.utils import create_tables, explode_db_uri
from critiquebrainz.data.export_manager import manager as export_manager
import critiquebrainz.data.fixtures as _fixtures
import subprocess

manager = Manager(create_app)

manager.add_command('export', export_manager)


@manager.command
def create_db():
    """Create and configure the database."""
    init_postgres(current_app.config['SQLALCHEMY_DATABASE_URI'])


@manager.command
def tables():
    create_tables(current_app)


@manager.command
def fixtures():
    """Update the newly created database with default schema and testing data."""
    _fixtures.install(current_app, *_fixtures.all_data)


def init_postgres(db_uri):
    """Initializes PostgreSQL database from provided URI.

    New user and database will be created, if needed. It also creates uuid-ossp extension.
    """
    hostname, db, username, password = explode_db_uri(db_uri)
    if hostname not in ['localhost', '127.0.0.1']:
        raise Exception('Cannot configure a remote database')

    # Checking if user already exists
    retv = subprocess.check_output('sudo -u postgres psql -t -A -c "SELECT COUNT(*) FROM pg_user WHERE usename = \'%s\';"' % username, shell=True)
    if retv[0] == '0':
        exit_code = subprocess.call('sudo -u postgres psql -c "CREATE ROLE %s PASSWORD \'%s\' NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN;"' % (username, password), shell=True)
        if exit_code != 0:
            raise Exception('Failed to create PostgreSQL user!')

    # Checking if database exists
    exit_code = subprocess.call('sudo -u postgres psql -c "\q" %s' % db, shell=True)
    if exit_code != 0:
        exit_code = subprocess.call('sudo -u postgres createdb -O %s %s' % (username, db), shell=True)
        if exit_code != 0:
            raise Exception('Failed to create PostgreSQL database!')

    # Creating database extension
    exit_code = subprocess.call('sudo -u postgres psql -t -A -c "CREATE EXTENSION IF NOT EXISTS \\"%s\\";" %s' % ('uuid-ossp', db), shell=True)
    if exit_code != 0:
        raise Exception('Failed to create PostgreSQL extension!')


if __name__ == '__main__':
    manager.run()
