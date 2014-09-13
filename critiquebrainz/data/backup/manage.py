from __future__ import print_function
from flask.ext.script import Manager
from flask import current_app, jsonify
from flask.json import JSONEncoder
from datetime import datetime
from time import gmtime, strftime
import errno
import unicodedata
import tarfile
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
def dump_db(location=os.path.join(os.getcwd(), 'backup'), rotate=False):
    """Create complete dump of PostgreSQL database.

    This command creates database dump using pg_dump and puts it into specified directory
    (default is *backup*). It's also possible to remove all previously created backups
    except two most recent ones. If you want to do that, set *rotate* argument to True.

    File with a dump will be a tar archive with a timestamp in the name: `%Y%m%d-%H%M%S.tar.bz2`.
    """

    # Creating backup directory, if needed
    create_path(location)

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

    print('Created %s.tar.bz2' % dump_file)

    if rotate:
        # Removing old backups (except two latest)
        print("Removing old backups...")
        entries = [os.path.join(location, f) for f in os.listdir(location)]
        pattern = re.compile("%s[0-9]+-[0-9]+.tar" % FILE_PREFIX)
        archives = filter(lambda x: pattern.search(x), entries)  # Selecting only our backup files
        archives.sort(key=lambda x: os.path.getmtime(x))  # Sorting by creation time
        for old_archive in archives[:-2]:
            print(' -', old_archive)
            os.remove(old_archive)

    print("Done!")


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
def dump_json(location=os.path.join(os.getcwd(), 'dump'), rotate=False):
    """Create JSON dumps with all reviews.

    This command will create an archive for each license available on CB.
    Archives will be put into a specified directory (default is *dump*).
    """
    current_app.json_encoder = DumpJSONEncoder

    print("Creating new archives...")
    for license in License.query.all():
        safe_name = slugify(license.id)
        license_dir = '%s/%s' % (location, safe_name)
        create_path(license_dir)

        # Finding release groups that have reviews with current license
        query = db.session.query(Review.release_group).group_by(Review.release_group)
        for release_group in query.all():
            release_group = release_group[0]
            # Creating directory structure for release group and dumping reviews
            rg_dir_part = '%s/%s' % (release_group[0:1], release_group[0:2])
            reviews = Review.list(release_group, license_id=license.id)[0]
            if len(reviews) > 0:
                rg_dir = '%s/%s' % (license_dir, rg_dir_part)
                create_path(rg_dir)
                f = open('%s/%s.json' % (rg_dir, release_group), 'w+')
                f.write(jsonify(reviews=[r.to_dict() for r in reviews]).data)
                f.close()

        # Copying legal text
        try:
            shutil.copyfile("critiquebrainz/data/licenses/%s.txt" % safe_name, '%s/COPYING' % license_dir)
        except IOError:
            print("Failed to copy license text for %s!" % license.id)

        create_tarball("%s/critiquebrainz-%s-%s-json.tar.bz2" % (location, datetime.today().strftime('%Y%m%d'), safe_name), license_dir)
        subprocess.call('rm -rf %s' % license_dir, shell=True)  # Cleanup
        print(" + %s/critiquebrainz-%s-%s-json.tar.bz2" % (location, datetime.today().strftime('%Y%m%d'), safe_name))

    if rotate:
        # Removing old backups
        print("Removing old archives...")
        entries = [os.path.join(location, f) for f in os.listdir(location)]
        pattern = re.compile("critiquebrainz-[0-9]+-[-\w]+-json.tar.bz2")
        archives = filter(lambda x: pattern.search(x), entries)  # Selecting only our backup files
        archives.sort(key=lambda x: os.path.getmtime(x))  # Sorting by creation time
        # Leaving only two latest sets of archives
        for old_archive in archives[:(-2 * License.query.count())]:
            print(' -', old_archive)
            os.remove(old_archive)

    print("Done!")


@backup_manager.command
def export(location=os.path.join(os.getcwd(), 'export'), rotate=False):
    print("Creating new archives...")
    time_now = datetime.today()

    # Getting psycopg2 cursor
    cursor = db.session.connection().connection.cursor()

    # Creating a directory where all dumps will go
    dump_dir = '%s/%s' % (location, time_now.strftime('%Y%m%d-%H%M%S'))
    create_path(dump_dir)

    # BASE ARCHIVE
    # Archiving stuff that is independent from licenses (users, licenses)
    base_archive_dir = '%s/cbdump' % dump_dir
    create_path(base_archive_dir)

    # Dumping tables
    base_archive_tables_dir = '%s/cbdump' % base_archive_dir
    create_path(base_archive_tables_dir)
    with open('%s/base_archive_tables_dir' % base_archive_tables_dir, 'w') as f:
         cursor.copy_to(f, '"user"', columns=('id', 'display_name', 'created', 'musicbrainz_id'))
    with open('%s/license' % base_archive_tables_dir, 'w') as f:
        cursor.copy_to(f, 'license')

    # Creating additional information about this archive
    try:
        # Copying the most restrictive license there (CC BY-NC-SA 3.0)
        shutil.copyfile("critiquebrainz/data/licenses/cc-by-nc-sa-30.txt", '%s/COPYING' % base_archive_dir)
    except IOError:
        print("Failed to copy CC BY-NC-SA 3.0 license text!")
    with open('%s/TIMESTAMP' % base_archive_dir, 'w') as f:
        f.write(time_now.isoformat(' '))
    with open('%s/SCHEMA_SEQUENCE' % base_archive_dir, 'w') as f:
        f.write(str(model.__version__))

    # Creating archive
    create_tarball("%s/cbdump.tar.bz2" % dump_dir, base_archive_dir)
    subprocess.call('rm -rf %s' % base_archive_dir, shell=True)  # Cleanup
    print(" + %s/cbdump.tar.bz2" % dump_dir)

    # REVIEWS
    # Archiving review tables (review, revision)

    # 1. COMBINED
    # Archiving all reviews (any license)
    reviews_combined_archive_dir = '%s/cbdump-reviews-all' % dump_dir
    create_path(reviews_combined_archive_dir)

    # Dumping tables
    reviews_combined_tables_dir = '%s/cbdump' % reviews_combined_archive_dir
    create_path(reviews_combined_tables_dir)
    with open('%s/review' % reviews_combined_tables_dir, 'w') as f:
        cursor.copy_to(f, 'review')
    with open('%s/revision' % reviews_combined_tables_dir, 'w') as f:
        cursor.copy_to(f, 'revision')

    # Creating additional information about this archive
    try:
        # Copying the most restrictive license there (CC BY-NC-SA 3.0)
        shutil.copyfile("critiquebrainz/data/licenses/cc-by-nc-sa-30.txt", '%s/COPYING' % reviews_combined_tables_dir)
    except IOError:
        print("Failed to copy CC BY-NC-SA 3.0 license text!")
    with open('%s/TIMESTAMP' % reviews_combined_tables_dir, 'w') as f:
        f.write(time_now.isoformat(' '))
    with open('%s/SCHEMA_SEQUENCE' % reviews_combined_tables_dir, 'w') as f:
        f.write(str(model.__version__))

    # Creating archive
    create_tarball("%s/cbdump-reviews-all.tar.bz2" % dump_dir, reviews_combined_archive_dir)
    subprocess.call('rm -rf %s' % reviews_combined_archive_dir, shell=True)  # Cleanup
    print(" + %s/cbdump-reviews-all.tar.bz2" % dump_dir)

    # 2. SEPARATE
    # Creating separate archives for each license
    for license in License.query.all():
        safe_name = slugify(license.id)
        license_dir = '%s/%s' % (dump_dir, safe_name)

        # Dumping tables
        tables_dir = '%s/cbdump' % license_dir
        create_path(tables_dir)
        with open('%s/review' % tables_dir, 'w') as f:
            cursor.copy_to(f, "(SELECT * FROM review WHERE license_id = '%s')" % license.id)
        with open('%s/revision' % tables_dir, 'w') as f:
            # TODO: Select only revisions for reviews with current license
            cursor.copy_to(f, 'revision')

        # Creating additional information about this archive
        try:
            shutil.copyfile("critiquebrainz/data/licenses/%s.txt" % safe_name, '%s/COPYING' % license_dir)
        except IOError:
            print("Failed to copy license text for %s!" % license.id)
        with open('%s/TIMESTAMP' % license_dir, 'w') as f:
            f.write(time_now.isoformat(' '))
        with open('%s/SCHEMA_SEQUENCE' % license_dir, 'w') as f:
            f.write(str(model.__version__))

        # Creating archive
        create_tarball("%s/cbdump-reviews-%s.tar.bz2" % (dump_dir, safe_name), license_dir)
        subprocess.call('rm -rf %s' % license_dir, shell=True)  # Cleanup
        print(" + %s/cbdump-reviews-%s.tar.bz2" % (dump_dir, safe_name))

    if rotate:
        # Removing old dumps
        print("Removing old dumps...")
        entries = [os.path.join(location, f) for f in os.listdir(location)]
        pattern = re.compile("[0-9]+-[0-9]+")
        entries = filter(lambda x: pattern.search(x), entries)
        entries = filter(os.path.isdir, entries)
        entries.sort()
        # Leaving only two latest sets of archives
        for old_dump in entries[:(-2)]:
            print(' -', old_dump)
            shutil.rmtree(old_dump)

    print("Done!")


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


def create_tarball(archive_name, source_dir):
    """Creates bzip2 compressed tarball of the specified source directory."""
    with tarfile.open(archive_name, "w:bz2") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
