from time import gmtime, strftime
from datetime import datetime
from functools import wraps
import subprocess
import tempfile
import tarfile
import shutil
import errno
import sys
import os
from flask import current_app, jsonify
from flask.json import JSONEncoder
from critiquebrainz.data.utils import create_path, remove_old_archives, slugify, explode_db_uri
from critiquebrainz.db import license as db_license, review as db_review
from critiquebrainz import frontend, db
import sqlalchemy
import click


cli = click.Group()


_TABLES = {
    "review": (
        "id",
        "entity_id",
        "entity_type",
        "user_id",
        "edits",
        "is_draft",
        "is_hidden",
        "license_id",
        "language",
        "source",
        "source_url",
    ),
    "revision": (
        "id",
        "review_id",
        "timestamp",
        "text",
    ),
    "license": (
        "id",
        "full_name",
        "info_url",
    ),
    "user": (
        "id",
        "display_name",
        "email",
        "created",
        "musicbrainz_id",
        "show_gravatar",
        "is_blocked",
        "spam_reports",
        "clients",
        "grants",
        "tokens"
    ),
}


def with_request_context(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        with frontend.create_app().test_request_context():
            return f(*args, **kwargs)
    return decorated


def has_data(table_name):
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT COUNT(*)
              FROM "{table_name}"
        """.format(table_name=table_name)))
        return result.fetchone()[0] > 0


@cli.command()
@click.option("--location", "-l", default=os.path.join("/", "data", "export", "full"), show_default=True,
              help="Directory where dumps need to be created")
@click.option("--rotate", "-r", is_flag=True)
@with_request_context
def full_db(location, rotate=False):
    """Create complete dump of PostgreSQL database.

    This command creates database dump using pg_dump and puts it into specified directory
    (default is *backup*). It's also possible to remove all previously created backups
    except two most recent ones. If you want to do that, set *rotate* argument to True.

    File with a dump will be a tar archive with a timestamp in the name: `%Y%m%d-%H%M%S.tar.bz2`.
    """
    create_path(location)

    FILE_PREFIX = "cb-backup-"
    db_hostname, db_port, db_name, db_username, _ = \
        explode_db_uri(current_app.config['SQLALCHEMY_DATABASE_URI'])

    print('Creating database dump in "%s"...' % location)

    # Executing pg_dump command
    # More info about it is available at http://www.postgresql.org/docs/9.3/static/app-pgdump.html
    dump_file = os.path.join(location, FILE_PREFIX + strftime("%Y%m%d-%H%M%S", gmtime()))
    print('pg_dump -h "%s" -p "%s" -U "%s" -d "%s" -Ft > "%s.tar"' %
          (db_hostname, db_port, db_username, db_name, dump_file),)
    result = subprocess.call(
        'pg_dump -h "%s" -p "%s" -U "%s" -d "%s" -Ft > "%s.tar"' %
        (db_hostname, db_port, db_username, db_name, dump_file),
        shell=True,
    )
    if result != 0:
        raise Exception("Failed to create database dump!")

    # Compressing created dump
    result = subprocess.call('bzip2 "%s.tar"' % dump_file, shell=True)
    if result != 0:
        raise Exception("Failed to create database dump!")

    print('Created %s.tar.bz2' % dump_file)

    if rotate:
        print("Removing old backups (except two latest)...")
        remove_old_archives(location, "%s[0-9]+-[0-9]+.tar" % FILE_PREFIX,
                            is_dir=False, sort_key=os.path.getmtime)

    print("Done!")


@cli.command()
@click.option("--location", "-l", default=os.path.join("/", "data", "export", "json"), show_default=True,
              help="Directory where dumps need to be created")
@click.option("--rotate", "-r", is_flag=True)
@with_request_context
def json(location, rotate=False):
    """Create JSON dumps with all reviews.

    This command will create an archive for each license available on CB.
    Archives will be put into a specified directory (default is *dump*).
    """
    create_path(location)

    current_app.json_encoder = DumpJSONEncoder

    print("Creating new archives...")
    for license in db_license.list_licenses():
        safe_name = slugify(license["id"])
        with tarfile.open(os.path.join(location, "critiquebrainz-%s-%s-json.tar.bz2" %
                                       (datetime.today().strftime('%Y%m%d'), safe_name)), "w:bz2") as tar:
            temp_dir = tempfile.mkdtemp()
            license_dir = os.path.join(temp_dir, safe_name)
            create_path(license_dir)

            # Finding entities that have reviews with current license
            entities = db_review.distinct_entities()
            for entity in entities:
                entity = str(entity)
                # Creating directory structure and dumping reviews
                dir_part = os.path.join(entity[0:1], entity[0:2])
                reviews = db_review.list_reviews(entity_id=entity, license_id=license["id"], limit=None)[0]
                if reviews:
                    rg_dir = '%s/%s' % (license_dir, dir_part)
                    create_path(rg_dir)
                    f = open('%s/%s.json' % (rg_dir, entity), 'w+')
                    f.write(jsonify(reviews=[db_review.to_dict(r) for r in reviews]).data.decode("utf-8"))
                    f.close()

            tar.add(license_dir, arcname='reviews')

            # Copying legal text
            tar.add(os.path.join("critiquebrainz", "data", "licenses", safe_name + ".txt"), arcname='COPYING')

            print(" + %s/critiquebrainz-%s-%s-json.tar.bz2" % (location, datetime.today().strftime('%Y%m%d'), safe_name))

            shutil.rmtree(temp_dir)  # Cleanup

    if rotate:
        print("Removing old sets of archives (except two latest)...")
        remove_old_archives(location, "critiquebrainz-[0-9]+-[-\w]+-json.tar.bz2",
                            is_dir=False, sort_key=os.path.getmtime)

    print("Done!")


@cli.command()
@click.option("--location", "-l", default=os.path.join("/", "data", "export", "public"), show_default=True,
              help="Directory where dumps need to be created")
@click.option("--rotate", "-r", is_flag=True)
@with_request_context
def public(location, rotate=False):
    """Creates a set of archives with public data.

    1. Base archive with license-independent data (users, licenses).
    2. Archive with all reviews and revisions.
    3... Separate archives for each license (contain reviews and revisions associated with specific license).
    """
    print("Creating public database dump...")
    time_now = datetime.today()

    connection = db.engine.raw_connection()
    cursor = connection.cursor()

    # Creating a directory where all dumps will go
    dump_dir = os.path.join(location, time_now.strftime('%Y%m%d-%H%M%S'))
    create_path(dump_dir)

    temp_dir = tempfile.mkdtemp()

    # Preparing meta files
    with open(os.path.join(temp_dir, 'TIMESTAMP'), 'w') as f:
        f.write(time_now.isoformat(' '))
    with open(os.path.join(temp_dir, 'SCHEMA_SEQUENCE'), 'w') as f:
        f.write(str(db.SCHEMA_VERSION))

    # BASE ARCHIVE
    # Archiving stuff that is independent from licenses (users, licenses)
    with tarfile.open(os.path.join(dump_dir, "cbdump.tar.bz2"), "w:bz2") as tar:
        base_archive_dir = os.path.join(temp_dir, 'cbdump')
        create_path(base_archive_dir)

        # Dumping tables
        base_archive_tables_dir = os.path.join(base_archive_dir, 'cbdump')
        create_path(base_archive_tables_dir)
        with open(os.path.join(base_archive_tables_dir, 'user_sanitised'), 'w') as f:
            cursor.copy_to(f, '"user"', columns=('id', 'created', 'display_name', 'musicbrainz_id'))
        with open(os.path.join(base_archive_tables_dir, 'license'), 'w') as f:
            cursor.copy_to(f, 'license', columns=_TABLES["license"])
        tar.add(base_archive_tables_dir, arcname='cbdump')

        # Including additional information about this archive
        # Copying the most restrictive license there (CC BY-NC-SA 3.0)
        tar.add(os.path.join('critiquebrainz', 'data', 'licenses', 'cc-by-nc-sa-30.txt'), arcname='COPYING')
        tar.add(os.path.join(temp_dir, 'TIMESTAMP'), arcname='TIMESTAMP')
        tar.add(os.path.join(temp_dir, 'SCHEMA_SEQUENCE'), arcname='SCHEMA_SEQUENCE')

        print(" + %s/cbdump.tar.bz2" % dump_dir)

    # REVIEWS
    # Archiving review tables (review, revision)

    # 1. COMBINED
    # Archiving all reviews (any license)
    REVISION_COMBINED_SQL = """
        SELECT {columns} FROM revision JOIN review
            ON review.id = revision.review_id
         WHERE review.is_hidden = false AND review.is_draft = false
    """.format(columns=', '.join(['revision.' + col for col in _TABLES["revision"]]))
    with tarfile.open(os.path.join(dump_dir, "cbdump-reviews-all.tar.bz2"), "w:bz2") as tar:
        # Dumping tables
        reviews_combined_tables_dir = os.path.join(temp_dir, 'cbdump-reviews-all')
        create_path(reviews_combined_tables_dir)
        with open(os.path.join(reviews_combined_tables_dir, 'review'), 'w') as f:
            cursor.copy_to(f, "(SELECT {columns} FROM review WHERE is_hidden = false AND is_draft = false)"
                           .format(columns=', '.join(_TABLES["review"])))
        with open(os.path.join(reviews_combined_tables_dir, 'revision'), 'w') as f:
            cursor.copy_to(f, "({sql})".format(sql=REVISION_COMBINED_SQL))
        tar.add(reviews_combined_tables_dir, arcname='cbdump')

        # Including additional information about this archive
        # Copying the most restrictive license there (CC BY-NC-SA 3.0)
        tar.add(os.path.join('critiquebrainz', 'data', 'licenses', 'cc-by-nc-sa-30.txt'), arcname='COPYING')
        tar.add(os.path.join(temp_dir, 'TIMESTAMP'), arcname='TIMESTAMP')
        tar.add(os.path.join(temp_dir, 'SCHEMA_SEQUENCE'), arcname='SCHEMA_SEQUENCE')

        print(" + %s/cbdump-reviews-all.tar.bz2" % dump_dir)

    # 2. SEPARATE
    # Creating separate archives for each license
    for license in db_license.list_licenses():
        safe_name = slugify(license["id"])
        with tarfile.open(os.path.join(dump_dir, "cbdump-reviews-%s.tar.bz2" % safe_name), "w:bz2") as tar:
            # Dumping tables
            tables_dir = os.path.join(temp_dir, safe_name)
            create_path(tables_dir)
            with open(os.path.join(tables_dir, 'review'), 'w') as f:
                cursor.copy_to(f, """(
                    SELECT {columns}
                      FROM review
                     WHERE is_hidden = false
                       AND is_draft = false
                       AND license_id = '{license_id}'
                )""".format(columns=', '.join(_TABLES["review"]), license_id=license["id"]))
            with open(os.path.join(tables_dir, 'revision'), 'w') as f:
                cursor.copy_to(f, """({REVISION_COMBINED_SQL} AND review.license_id='{license_id}')"""
                               .format(REVISION_COMBINED_SQL=REVISION_COMBINED_SQL, license_id=license["id"]))
            tar.add(tables_dir, arcname='cbdump')

            # Including additional information about this archive
            tar.add(os.path.join("critiquebrainz", "data", "licenses", safe_name + ".txt"), arcname='COPYING')
            tar.add(os.path.join(temp_dir, 'TIMESTAMP'), arcname='TIMESTAMP')
            tar.add(os.path.join(temp_dir, 'SCHEMA_SEQUENCE'), arcname='SCHEMA_SEQUENCE')

        print(" + %s/cbdump-reviews-%s.tar.bz2" % (dump_dir, safe_name))

    shutil.rmtree(temp_dir)  # Cleanup
    connection.close()

    if rotate:
        print("Removing old dumps (except two latest)...")
        remove_old_archives(location, "[0-9]+-[0-9]+", is_dir=True)

    print("Done!")


@cli.command(name="import")
@click.argument("archive", type=click.Path(exists=True), required=True)
@with_request_context
def importer(archive):
    """Imports database dump (archive) produced by export command.

    Before importing make sure that all required data is already imported or exists in the archive. For example,
    importing will fail if you'll try to import review without users or licenses. Same applies to revisions. To get more
    information about various dependencies see database schema.

    You should only import data into empty tables. Data will not be imported into tables that already have rows. This is
    done to prevent conflicts. Feel free improve current implementation. :)

    Importing only supported for bzip2 compressed tar archives. It will fail if version of the schema that provided
    archive requires is different from the current. Make sure you have the latest dump available.
    """
    with tarfile.open(archive, 'r:bz2') as archive:
        # TODO(roman): Read data from the archive without extracting it into temporary directory.
        temp_dir = tempfile.mkdtemp()
        archive.extractall(temp_dir)

        # Verifying schema version
        try:
            with open(os.path.join(temp_dir, 'SCHEMA_SEQUENCE')) as f:
                archive_version = f.readline()
                if archive_version != str(db.SCHEMA_VERSION):
                    sys.exit("Incorrect schema version! Expected: %d, got: %c."
                             "Please, get the latest version of the dump."
                             % (db.SCHEMA_VERSION, archive_version))
        except IOError as exception:
            if exception.errno == errno.ENOENT:
                print("Can't find SCHEMA_SEQUENCE in the specified archive. Importing might fail.")
            else:
                sys.exit("Failed to open SCHEMA_SEQUENCE file. Error: %s" % exception)

        # Importing data
        import_data(os.path.join(temp_dir, 'cbdump', 'user_sanitised'), 'user',
                    columns=('id', 'created', 'display_name', 'musicbrainz_id'))
        import_data(os.path.join(temp_dir, 'cbdump', 'license'), 'license')
        import_data(os.path.join(temp_dir, 'cbdump', 'review'), 'review')
        import_data(os.path.join(temp_dir, 'cbdump', 'revision'), 'revision')

        shutil.rmtree(temp_dir)  # Cleanup
        print("Done!")


def import_data(file_name, table_name, columns=None):

    connection = db.engine.raw_connection()
    try:
        cursor = connection.cursor()

        # Checking if table already contains any data
        if has_data(table_name):
            print("Table %s already contains data. Skipping." % table_name)
            return

        # Checking if the specified file exists or if the file is empty
        if not os.path.exists(file_name) or os.stat(file_name).st_size == 0:
            print("Can't find data file for %s table. Skipping." % table_name)
            return

        # and if it doesn't, trying to import data
        print("Importing data into %s table." % table_name)
        with open(file_name, 'r') as f:
            if columns is None:
                columns = _TABLES[table_name]
            cursor.copy_from(f, '"{table_name}"'.format(table_name=table_name), columns=columns)
            connection.commit()

    finally:
        connection.close()


class DumpJSONEncoder(JSONEncoder):
    """Custom JSON encoder for database dumps."""

    def default(self, o):  # pylint: disable=method-hidden
        try:
            if isinstance(o, datetime):
                return o.isoformat()
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, o)
