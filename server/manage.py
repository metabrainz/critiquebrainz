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
    """Update the newly created database with default schema and testing data"""
    _fixtures.install(app, *_fixtures.all_data)


@manager.command
def create_db():
    """Create and configure the database"""
    from os import system
    def explode_url(url):
        from urlparse import urlsplit
        url = urlsplit(url)
        username = url.username
        password = url.password
        db = url.path[1:]
        hostname = url.hostname
        return hostname, db, username, password

    hostname, db, username, password = explode_url(app.config['SQLALCHEMY_DATABASE_URI'])
    if hostname not in ['localhost', '127.0.0.1']:
        raise Exception('Cannot configure a remote database')
    
    exit_code = system('scripts/create_database_user.sh %s %s' % (username, password))
    if exit_code != 0: 
        raise Exception('Failed to create PostgreSQL user')
    
    exit_code = system('scripts/create_database.sh %s %s' % (db, username))
    if exit_code != 0: 
        raise Exception('Failed to create PostgreSQL database')
    
    exit_code = system('scripts/create_database_extension.sh %s %s' % (db, 'uuid-ossp'))
    if exit_code != 0: 
        raise Exception('Failed to create PostgreSQL extension')


if __name__ == '__main__':
    manager.run()

