#!/usr/bin/python
from __future__ import print_function
import subprocess
import os
import re
from datetime import datetime
from time import gmtime, strftime
from flask.json import JSONEncoder
from flask.ext.script import Manager

from critiquebrainz import fixtures as _fixtures
from critiquebrainz import app, db

manager = Manager(app)


class DumpJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
app.json_encoder = DumpJSONEncoder


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
def backup_db(location=os.path.join(os.path.dirname(__file__), 'backup'), clean=False):
    """Create database backup."""

    # Creating backup directory if needed
    exit_code = subprocess.call('mkdir -p %s' % location, shell=True)
    if exit_code != 0:
        raise Exception("Failed to backup directory!")

    file_prefix = "cb-backup-"

    # Creating database dump
    print("Creating database dump...")
    file_name = "%s/%s%s" % (location, file_prefix, strftime("%Y%m%d-%H%M%S", gmtime()))
    hostname, db, username, password = explode_url(app.config['SQLALCHEMY_DATABASE_URI'])
    print('pg_dump -Ft "%s" > "%s.tar"' % (db, file_name))
    exit_code = subprocess.call('pg_dump -Ft "%s" > "%s.tar"' % (db, file_name), shell=True)
    if exit_code == 0:
        exit_code = subprocess.call('bzip2 "%s.tar"' % file_name, shell=True)
    if exit_code != 0:
        raise Exception("Failed to create database dump!")
    print('Done! Created "%s.tar.bz2".' % file_name)

    if clean:
        # Removing old backups (except two latest)
        files = [os.path.join(location, f) for f in os.listdir(location)]

        pattern = re.compile("%s[0-9]+-[0-9]+.tar" % file_prefix)
        def is_backup_archive(file_name):
            return pattern.search(file_name)

        archives = filter(is_backup_archive, files)
        files.sort(key=lambda x: os.path.getmtime(x))

        for archive in archives[:-2]:
            print("Deleting old backup file:", archive)
            os.remove(archive)


@manager.command
def dump_json():
    """Create JSON dump of all reviews."""
    import shutil
    from flask import jsonify
    from critiquebrainz.fixtures import LicenseData
    from critiquebrainz.db.review import Review
    from critiquebrainz.db import db

    dump_dir = 'dump'
    by_sa_dir = 'critiquebrainz-json-by-sa'
    exit_code = subprocess.call('mkdir -p %s/%s' % (dump_dir, by_sa_dir), shell=True)
    if exit_code != 0:
        raise Exception("Failed to create directory!")
    by_nc_sa_dir = 'critiquebrainz-json-by-nc-sa'
    exit_code = subprocess.call('mkdir -p %s/%s' % (dump_dir, by_nc_sa_dir), shell=True)
    if exit_code != 0:
        raise Exception("Failed to create directory!")

    # Creating JSON dumps
    query = db.session.query(Review.release_group).group_by(Review.release_group)
    for release_group in query.all():
        release_group = release_group[0]
        rg_dir_part = '%s/%s' % (release_group[0:1], release_group[0:2])

        # CC BY-SA reviews
        reviews = Review.list(release_group, license_id=LicenseData.cc_by_sa_3.id)[0]
        if len(reviews) > 0:
            json = jsonify(reviews=[r.to_dict(['user'], is_dump=True) for r in reviews]).data
            rg_dir = '%s/%s/%s' % (dump_dir, by_sa_dir, rg_dir_part)
            exit_code = subprocess.call('mkdir -p %s' % rg_dir, shell=True)
            if exit_code != 0:
                raise Exception("Failed to create directory!")
            f = open('%s/%s.json' % (rg_dir, release_group), 'w+')
            f.write(json)
            f.close()

        # CC BY-NC-SA reviews
        reviews = Review.list(release_group, license_id=LicenseData.cc_by_nc_sa_3.id)[0]
        if len(reviews) > 0:
            json = jsonify(reviews=[r.to_dict(['user'], is_dump=True) for r in reviews]).data
            rg_dir = '%s/%s/%s' % (dump_dir, by_nc_sa_dir, rg_dir_part)
            exit_code = subprocess.call('mkdir -p %s' % rg_dir, shell=True)
            if exit_code != 0:
                raise Exception("Failed to create directory!")
            f = open('%s/%s.json' % (rg_dir, release_group), 'w+')
            f.write(json)
            f.close()

    # Copying legal stuff
    shutil.copyfile("licenses/cc-by-sa.txt", '%s/%s/COPYING' % (dump_dir, by_sa_dir))
    shutil.copyfile("licenses/cc-by-nc-sa.txt", '%s/%s/COPYING' % (dump_dir, by_nc_sa_dir))

    # Creating archives
    exit_code = subprocess.call('tar -cjf dump/critiquebrainz-json-cc-by-sa.tar.bz2 -C "%s" %s' % (dump_dir, by_sa_dir), shell=True)
    if exit_code != 0:
        raise Exception("Failed to create an archive for CC BY-SA reviews!")
    exit_code = subprocess.call('tar -cjf dump/critiquebrainz-json-cc-by-nc-sa.tar.bz2 -C "%s" %s' % (dump_dir, by_nc_sa_dir), shell=True)
    if exit_code != 0:
        raise Exception("Failed to create an archive for CC BY-NC-SA reviews!")

    # Cleanup
    subprocess.call('rm -rf %s/%s' % (dump_dir, by_sa_dir), shell=True)
    subprocess.call('rm -rf %s/%s' % (dump_dir, by_nc_sa_dir), shell=True)


@manager.command
def create_db():
    """Create and configure the database."""
    init_postgres(app.config['SQLALCHEMY_DATABASE_URI'])


if __name__ == '__main__':
    manager.run()

