#!/usr/bin/python
import subprocess
from flask.ext.script import Manager

from critiquebrainz import fixtures as _fixtures
from critiquebrainz import app, db

manager = Manager(app)


def init_postgres(uri):
    def explode_url(url):
        from urlparse import urlsplit
        url = urlsplit(url)
        username = url.username
        password = url.password
        db = url.path[1:]
        hostname = url.hostname
        return hostname, db, username, password

    hostname, db, username, password = explode_url(uri)
    if hostname not in ['localhost', '127.0.0.1']:
        raise Exception('Cannot configure a remote database')

    # Checking if user already exists
    retv = subprocess.check_output('psql -U postgres -h %s -t -A -c "SELECT COUNT(*) FROM pg_user WHERE usename = \'%s\';"' % (hostname, username), shell=True)
    if retv[0] == '0':
        exit_code = subprocess.call('psql -U postgres -h %s -c "CREATE ROLE %s PASSWORD \'%s\' NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN;"' % (hostname, username, password), shell=True)
        if exit_code != 0:
            raise Exception('Failed to create PostgreSQL user!')

    # Checking if database exists
    exit_code = subprocess.call('psql -U postgres -h %s -c "\q" %s' % (hostname, db), shell=True)
    if exit_code != 0:
        exit_code = subprocess.call('createdb -U postgres -h %s -O %s %s' % (hostname, username, db), shell=True)
        if exit_code != 0:
            raise Exception('Failed to create PostgreSQL database!')

    # Creating database extension
    exit_code = subprocess.call('psql -U postgres -h %s -t -A -c "CREATE EXTENSION IF NOT EXISTS \\"%s\\";" %s' % (hostname, 'uuid-ossp', db), shell=True)
    if exit_code != 0:
        raise Exception('Failed to create PostgreSQL extension!')


@manager.command
def tables():
    db.create_tables(app)


@manager.command
def fixtures():
    """Update the newly created database with default schema and testing data"""
    _fixtures.install(app, *_fixtures.all_data)


@manager.command
def create_db():
    """Create and configure the database"""
    init_postgres(app.config['SQLALCHEMY_DATABASE_URI'])


if __name__ == '__main__':
    manager.run()

