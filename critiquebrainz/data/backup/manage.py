from __future__ import print_function
from flask.ext.script import Manager
from flask import current_app, jsonify
from flask.json import JSONEncoder
from datetime import datetime
from time import gmtime, strftime
from urlparse import urlsplit
import unicodedata
import shutil
import subprocess
import os
import re

from critiquebrainz.data import db
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.license import License

backup_manager = Manager()


@backup_manager.command
def dump_db(location=os.path.join(os.getcwd(), 'backup'), clean=False):
    """Create complete dump of PostgreSQL database."""

    # Creating backup directory, if needed
    exit_code = subprocess.call('mkdir -p %s' % location, shell=True)
    if exit_code != 0:
        raise Exception("Failed to create backup directory!")

    FILE_PREFIX = "cb-backup-"
    db_hostname, db_name, db_username, db_password = explode_db_url(current_app.config['SQLALCHEMY_DATABASE_URI'])

    print('Creating database dump in "%s"...' % location)

    # Executing pg_dump command
    dump_file = "%s/%s%s" % (location, FILE_PREFIX, strftime("%Y%m%d-%H%M%S", gmtime()))
    if subprocess.call('pg_dump -Ft "%s" > "%s.tar"' % (db_name, dump_file), shell=True) != 0:
        raise Exception("Failed to create database dump!")

    # Compressing created dump
    if subprocess.call('bzip2 "%s.tar"' % dump_file, shell=True) != 0:
        raise Exception("Failed to create database dump!")

    print('Done! Created "%s.tar.bz2".' % dump_file)

    if clean:
        # Removing old backups (except two latest)
        print('Removing old backups...')
        files = [os.path.join(location, f) for f in os.listdir(location)]
        pattern = re.compile("%s[0-9]+-[0-9]+.tar" % FILE_PREFIX)
        archives = filter(lambda x: pattern.search(x), files)  # Selecting only our backup files
        archives.sort(key=lambda x: os.path.getmtime(x))  # Sorting by creation time
        for old_archive in archives[:-2]:
            print(' - ', old_archive)
            os.remove(old_archive)


class DumpJSONEncoder(JSONEncoder):
    """Custom JSON encoder for database dumps."""
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


@backup_manager.command
def dump_json(location=os.path.join(os.getcwd(), 'dump')):
    """Create JSON dump with all reviews."""
    current_app.json_encoder = DumpJSONEncoder

    for license in License.query.all():
        safe_name = slugify(license.id)
        license_dir = '%s/%s' % (location, safe_name)

        exit_code = subprocess.call('mkdir -p %s' % license_dir, shell=True)
        if exit_code != 0:
            raise Exception("Failed to create directory for %s reviews!" % license.id)

        # Finding release groups that have reviews with current license
        query = db.session.query(Review.release_group).group_by(Review.release_group)
        for release_group in query.all():
            release_group = release_group[0]
            # Creating directory structure for release group and dumping reviews
            rg_dir_part = '%s/%s' % (release_group[0:1], release_group[0:2])
            reviews = Review.list(release_group, license_id=license.id)[0]
            if len(reviews) > 0:
                json = jsonify(reviews=[r.to_dict(['user']) for r in reviews]).data
                rg_dir = '%s/%s' % (license_dir, rg_dir_part)
                exit_code = subprocess.call('mkdir -p %s' % rg_dir, shell=True)
                if exit_code != 0:
                    raise Exception("Failed to create directory for release group!")
                f = open('%s/%s.json' % (rg_dir, release_group), 'w+')
                f.write(json)
                f.close()

        # Copying legal text
        try:
            shutil.copyfile("licenses/%s.txt" % safe_name, '%s/COPYING' % license_dir)
        except IOError:
            print("Failed to copy license text for %s!" % license.id)

        # Creating archive
        exit_code = subprocess.call('tar -cjf %s/critiquebrainz-json-%s.tar.bz2 -C "%s" %s' % (location, safe_name, location, safe_name), shell=True)
        if exit_code != 0:
            raise Exception("Failed to create an archive for %s reviews!" % license.id)

        # Cleanup
        subprocess.call('rm -rf %s' % license_dir, shell=True)


def slugify(value):
    """Converts to lowercase, removes alphanumerics and underscores, and converts spaces to hyphens.
    Also strips leading and trailing whitespace.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


def explode_db_url(url):
    url = urlsplit(url)
    return url.hostname, url.path[1:], url.username, url.password
