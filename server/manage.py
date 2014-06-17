#!/usr/bin/python
import subprocess
from flask.ext.script import Manager

from critiquebrainz import fixtures as _fixtures
from critiquebrainz import app, db

manager = Manager(app)

def explode_url(url):
    from urlparse import urlsplit
    url = urlsplit(url)
    username = url.username
    password = url.password
    db = url.path[1:]
    hostname = url.hostname
    return hostname, db, username, password

def init_postgres(uri):
    hostname, db, username, password = explode_url(uri)
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


@manager.command
def tables():
    db.create_tables(app)


@manager.command
def fixtures():
    """Update the newly created database with default schema and testing data."""
    _fixtures.install(app, *_fixtures.all_data)


@manager.command
def dump_db():
    """Create dump of the database."""
    import subprocess
    from time import gmtime, strftime
    backup_dir = 'backup'
    exit_code = subprocess.call('mkdir -p %s' % backup_dir, shell=True)
    if exit_code != 0:
        raise Exception("Failed to backup directory!")
    print "Creating database dump..."
    file_name = "%s/cb-%s" % (backup_dir, strftime("%Y%m%d-%H%M%S", gmtime()))
    hostname, db, username, password = explode_url(app.config['SQLALCHEMY_DATABASE_URI'])
    print 'pg_dump -Ft "%s" > "%s.tar"' % (db, file_name)
    exit_code = subprocess.call('pg_dump -Ft "%s" > "%s.tar"' % (db, file_name), shell=True)
    if exit_code == 0:
        exit_code = subprocess.call('bzip2 "%s.tar"' % file_name, shell=True)
    if exit_code != 0:
        raise Exception("Failed to create database dump!")
    print 'Done! Created "%s.tar.bz2".' % file_name


@manager.command
def create_db():
    """Create and configure the database."""
    init_postgres(app.config['SQLALCHEMY_DATABASE_URI'])


if __name__ == '__main__':
    manager.run()

