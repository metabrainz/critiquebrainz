from __future__ import print_function
from flask.ext.script import Manager
from flask import current_app, jsonify
from flask.json import JSONEncoder
from datetime import datetime
from time import gmtime, strftime
import errno
import unicodedata
import shutil
import subprocess
import os
import re

from critiquebrainz.data import db, explode_db_url
from critiquebrainz.data import model
from critiquebrainz.data.model.review import Review
from critiquebrainz.data.model.license import License

backup_manager = Manager()


@backup_manager.command
def backup_db(location=os.path.join(os.getcwd(), 'backup'), clean=False):
    """Create complete dump of PostgreSQL database.

    This command creates database dump using pg_dump and puts it into specified directory
    (default is *backup*). It's also possible to remove all previously created backups
    except two most recent ones. If you want to do that, set *clean* argument to True.

    File with a dump will be a tar archive with a timestamp in the name: `%Y%m%d-%H%M%S.tar.bz2`.
    """

    # Creating backup directory, if needed
    exit_code = subprocess.call('mkdir -p %s' % location, shell=True)
    if exit_code != 0:
        raise Exception("Failed to create backup directory!")

    FILE_PREFIX = "cb-backup-"
    db_hostname, db_name, db_username, db_password = explode_db_url(current_app.config['SQLALCHEMY_DATABASE_URI'])

    print('Creating database dump in "%s"...' % location)

    # Executing pg_dump command
    # More info about it is available at http://www.postgresql.org/docs/9.3/static/app-pgdump.html
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
    """Create JSON dumps with all reviews.

    This command will create an archive for each license available on CB.
    Archives will be put into a specified directory (default is *dump*).
    """
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
                rg_dir = '%s/%s' % (license_dir, rg_dir_part)
                exit_code = subprocess.call('mkdir -p %s' % rg_dir, shell=True)
                if exit_code != 0:
                    raise Exception("Failed to create directory for release group!")
                f = open('%s/%s.json' % (rg_dir, release_group), 'w+')
                f.write(jsonify(reviews=[r.to_dict() for r in reviews]).data)
                f.close()

        # Copying legal text
        try:
            shutil.copyfile("critiquebrainz/data/licenses/%s.txt" % safe_name, '%s/COPYING' % license_dir)
        except IOError:
            print("Failed to copy license text for %s!" % license.id)

        # Creating archive
        exit_code = subprocess.call('tar -cjf %s/critiquebrainz-json-%s.tar.bz2 -C "%s" %s' % (location, safe_name, location, safe_name), shell=True)
        if exit_code != 0:
            raise Exception("Failed to create an archive for %s reviews!" % license.id)

        # Cleanup
        subprocess.call('rm -rf %s' % license_dir, shell=True)


@backup_manager.command
def dump(location=os.path.join(os.getcwd(), 'dump')):
    # Getting psycopg2 cursor
    cursor = db.session.connection().connection.cursor()

    for license in License.query.all():
        safe_name = slugify(license.id)
        license_dir = '%s/%s' % (location, safe_name)
        tables_dir = '%s/cbdump' % license_dir
        create_path(tables_dir)

        # Dumping database tables
        with open('%s/user' % tables_dir, 'w') as f:
            cursor.copy_to(f, '"user"', columns=('id', 'display_name', 'created', 'musicbrainz_id'))
        with open('%s/license' % tables_dir, 'w') as f:
            cursor.copy_to(f, 'license')
        with open('%s/review' % tables_dir, 'w') as f:
            cursor.copy_to(f, "(SELECT * FROM review WHERE license_id = '%s')" % license.id)
        with open('%s/revision' % tables_dir, 'w') as f:
            cursor.copy_to(f, 'revision')

        # Copying legal text
        try:
            shutil.copyfile("critiquebrainz/data/licenses/%s.txt" % safe_name, '%s/COPYING' % license_dir)
        except IOError:
            print("Failed to copy license text for %s!" % license.id)

        time_now = datetime.today()
        with open('%s/TIMESTAMP' % license_dir, 'w') as f:
            f.write(time_now.isoformat(' '))

        with open('%s/SCHEMA_SEQUENCE' % license_dir, 'w') as f:
            f.write(str(model.__version__))

        # Creating archive
        exit_code = subprocess.call('tar -cjf %s/critiquebrainz-%s-%s-dump.tar.bz2 -C "%s" %s' %
                                    (location, time_now.strftime('%Y%m%d'), safe_name, location, safe_name), shell=True)
        if exit_code != 0:
            raise Exception("Failed to create an archive for %s reviews!" % license.id)

        # Cleanup
        subprocess.call('rm -rf %s' % license_dir, shell=True)

        print("Created dump with %s licensed reviews." % license.id)


def slugify(value):
    """Converts to lowercase, removes alphanumerics and underscores, and converts spaces to hyphens.
    Also strips leading and trailing whitespace.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


def create_path(path):
    """Creates a directory structure if it doesn't exist yet."""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
