from time import gmtime, strftime
from datetime import datetime
import subprocess
import tempfile
import tarfile
import shutil
import errno
import sys
import os
from flask import current_app, jsonify
from flask.json import JSONEncoder
import sqlalchemy
import click
from critiquebrainz.data.utils import create_path, remove_old_archives, slugify, explode_db_uri, with_request_context
from critiquebrainz.db import license as db_license, review as db_review
from critiquebrainz import db
from psycopg2.sql import SQL, Identifier


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
        "published_on",
        "source",
        "source_url",
    ),
    "revision": (
        "id",
        "review_id",
        "timestamp",
        "text",
        "rating",
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
        "license_choice",
        "spam_reports",
        "clients",
        "grants",
        "tokens"
    ),
    "avg_rating": (
        "entity_id",
        "entity_type",
        "rating",
        "count",
    ),
    "vote": (
        "user_id",
        "revision_id",
        "vote",
        "rated_at",
    ),
}


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
    with db.engine.begin() as connection:
        for license in db_license.get_licenses_list(connection):
            safe_name = slugify(license["id"])
            with tarfile.open(os.path.join(location, "critiquebrainz-%s-%s-json.tar.bz2" %
                                           (datetime.today().strftime('%Y%m%d'), safe_name)), "w:bz2") as tar:
                temp_dir = tempfile.mkdtemp()
                license_dir = os.path.join(temp_dir, safe_name)
                create_path(license_dir)

                # Finding entities that have reviews with current license
                entities = db_review.get_distinct_entities(connection)
                for entity in entities:
                    entity = str(entity)
                    # Creating directory structure and dumping reviews
                    dir_part = os.path.join(entity[0:1], entity[0:2])
                    reviews = db_review.get_reviews_list(connection, entity_id=entity, license_id=license["id"], limit=None)[0]
                    if reviews:
                        rg_dir = '%s/%s' % (license_dir, dir_part)
                        create_path(rg_dir)
                        f = open('%s/%s.json' % (rg_dir, entity), 'w+')
                        f.write(jsonify(reviews=[db_review.to_dict(r, connection=connection) for r in reviews])
                                .data.decode("utf-8"))
                        f.close()

                tar.add(license_dir, arcname='reviews')

                # Copying legal text
                tar.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), "licenses", safe_name + ".txt"),
                        arcname='COPYING')

                print(" + %s/critiquebrainz-%s-%s-json.tar.bz2" % (location, datetime.today().strftime('%Y%m%d'), safe_name))

                shutil.rmtree(temp_dir)  # Cleanup

        if rotate:
            print("Removing old sets of archives (except two latest)...")
            remove_old_archives(location, r"critiquebrainz-[0-9]+-[-\w]+-json.tar.bz2",
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

    # Creating a directory where all dumps will go
    dump_dir = os.path.join(location, time_now.strftime('%Y%m%d-%H%M%S'))
    create_path(dump_dir)

    # Prepare meta files
    meta_files_dir = tempfile.mkdtemp()
    prepare_meta_files(meta_files_dir, time_now=time_now)

    with db.engine.begin() as connection:
        # BASE ARCHIVE
        # Contains all license independent data (licenses, users)
        base_archive_path = create_base_archive(
            connection,
            location=dump_dir,
            meta_files_dir=meta_files_dir,
        )
        print(base_archive_path)

        # 1. COMBINED
        # Archiving all reviews (any license)
        review_dump_path = create_reviews_archive(
            connection,
            location=dump_dir,
            meta_files_dir=meta_files_dir,
        )
        print(review_dump_path)

        # 2. SEPARATE
        # Creating separate archives for each license
        for license in db_license.get_licenses_list(connection):
            review_dump_path = create_reviews_archive(
                connection,
                location=dump_dir,
                meta_files_dir=meta_files_dir,
                license_id=license['id'],
            )
            print(review_dump_path)

    shutil.rmtree(meta_files_dir)  # Cleanup
    if rotate:
        print("Removing old dumps (except two latest)...")
        remove_old_archives(location, "[0-9]+-[0-9]+", is_dir=True)

    print("Done!")


def prepare_meta_files(meta_files_dir, time_now=None):
    """Prepares the files containing meta information, namely the TIMESTAMP and the SCHEMA_SEQUENCE file.

    Args:
        meta_files_dir: Directory where the files needs to be created.
        time_now (optional): Specifies the timestamp to be copied to the TIMESTAMP file.
    """
    if not time_now:
        time_now = datetime.today()
    with open(os.path.join(meta_files_dir, 'TIMESTAMP'), 'w') as f:
        f.write(time_now.isoformat(' '))
    with open(os.path.join(meta_files_dir, 'SCHEMA_SEQUENCE'), 'w') as f:
        f.write(str(db.SCHEMA_VERSION))


def add_meta_files(tarfile, meta_files_dir):
    """Adds the meta files to the specified tarfile.

    Args:
        tarfile: The tarfile object where the files needs to be added.
        meta_files_dir: The directory containing the meta files.
    """
    tarfile.add(os.path.join(meta_files_dir, 'TIMESTAMP'), arcname='TIMESTAMP')
    tarfile.add(os.path.join(meta_files_dir, 'SCHEMA_SEQUENCE'), arcname='SCHEMA_SEQUENCE')


def create_base_archive(connection, *, location, meta_files_dir=None):
    """Creates a dump of all license-independent information: (users, license).

    Args:
        connection (sqlalchemy.engine.Connection): an sqlalchemy connection to the database for executing database queries
        location: Path of the directory where the archive needs to be created.
        meta_files_dir (optional): Path of the directory containing the meta files to be copied
            into the archive (TIMESTAMP and SCHEMA_VERSION). If not specified, the meta files are
            generated and added to the archive.
    Returns:
        Complete path to the created archive.
    """
    with tarfile.open(os.path.join(location, "cbdump.tar.bz2"), "w:bz2") as tar:
        temp_dir = tempfile.mkdtemp()
        base_archive_dir = os.path.join(temp_dir, 'cbdump')
        create_path(base_archive_dir)

        # Dumping tables
        base_archive_tables_dir = os.path.join(base_archive_dir, 'cbdump')
        create_path(base_archive_tables_dir)

        cursor = connection.connection.cursor()
        try:
            with open(os.path.join(base_archive_tables_dir, 'user_sanitised'), 'w') as f:
                cursor.copy_to(f, '"user"', columns=('id', 'created', 'display_name', 'musicbrainz_id'))
            with open(os.path.join(base_archive_tables_dir, 'license'), 'w') as f:
                cursor.copy_to(f, 'license', columns=_TABLES["license"])
        except Exception as e:
            print('Error "{}" occurred while copying tables during creation of the base archive!'.format(e))
            raise
        tar.add(base_archive_tables_dir, arcname='cbdump')

        # Including additional information about this archive
        # Copying the most restrictive license there (CC BY-NC-SA 3.0)
        tar.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), "licenses", "cc-by-nc-sa-30.txt"), arcname='COPYING')
        # Copy meta files
        if not meta_files_dir:
            prepare_meta_files(temp_dir)
            meta_files_dir = temp_dir
        add_meta_files(tar, meta_files_dir)

        shutil.rmtree(temp_dir)  # Cleanup
        return " + %s/cbdump.tar.bz2" % location


def create_reviews_archive(connection, *, location, meta_files_dir=None, license_id=None):
    """Creates a dump of reviews filtered on the given license_id, their revisions and
       the avg. rating tables.

    Args:
        connection (sqlalchemy.engine.Connection): an sqlalchemy connection to the database for executing database queries
        location: Path of the directory where the archive needs to be created.
        meta_files_dir (optional): Path of the directory containing the meta files to be copied
            into the archive (TIMESTAMP and SCHEMA_VERSION). If not specified, the meta files are
            generated and added to the archive.
        license_id (optional): The ID of the license whose reviews (and related information)
            is to be added to the dump. All reviews are copied (irrespective of their
            license) if license_id is None.
    Returns:
        Complete path to the created archive.
    """
    if license_id:
        license_where_clause = "AND license_id = '{}'".format(license_id)
        safe_name = slugify(license_id)
        archive_name = "cbdump-reviews-{}.tar.bz2".format(safe_name)
    else:
        license_where_clause = ''
        archive_name = "cbdump-reviews-all.tar.bz2"
        safe_name = 'cb-reviews-all'

    REVIEW_SQL = """(
        SELECT {columns}
          FROM review
         WHERE is_hidden = false
           AND is_draft = false
               {license_where_clause}
    )""".format(columns=', '.join(_TABLES["review"]), license_where_clause=license_where_clause)

    REVISION_SQL = """(
        SELECT {columns}
          FROM revision
          JOIN review
            ON review.id = revision.review_id
         WHERE review.is_hidden = false
           AND review.is_draft = false
               {license_where_clause}
    )""".format(
        columns=', '.join(['revision.' + column for column in _TABLES['revision']]),
        license_where_clause=license_where_clause,
    )

    VOTE_SQL = """(
        SELECT {columns}
          FROM vote
          JOIN ( SELECT revision.id
                   FROM revision
                   JOIN review
                     ON review.id = revision.review_id
                  WHERE review.is_hidden = false
                    AND review.is_draft = false
                        {license_where_clause}
                ) AS rev
            ON vote.revision_id = rev.id
    )""".format(
        columns=', '.join(['vote.' + column for column in _TABLES['vote']]),
        license_where_clause=license_where_clause,
    )

    with tarfile.open(os.path.join(location, archive_name), "w:bz2") as tar:
        # Dumping tables
        temp_dir = tempfile.mkdtemp()
        reviews_tables_dir = os.path.join(temp_dir, safe_name)
        create_path(reviews_tables_dir)

        cursor = connection.connection.cursor()
        try:
            with open(os.path.join(reviews_tables_dir, 'review'), 'w') as f:
                cursor.copy_to(f, REVIEW_SQL)

            with open(os.path.join(reviews_tables_dir, 'revision'), 'w') as f:
                cursor.copy_to(f, REVISION_SQL)

            with open(os.path.join(reviews_tables_dir, 'avg_rating'), 'w') as f:
                cursor.copy_to(f, "(SELECT {columns} FROM avg_rating)".format(columns=", ".join(_TABLES["avg_rating"])))

            with open(os.path.join(reviews_tables_dir, 'vote'), 'w') as f:
                cursor.copy_to(f, VOTE_SQL)

        except Exception as e:
            print("Error {} occurred while copying tables during the creation of the reviews archive!".format(e))
            raise
        tar.add(reviews_tables_dir, arcname='cbdump')

        if not license_id:
            tar.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), "licenses", "cc-by-nc-sa-30.txt"),
                    arcname='COPYING')
        else:
            tar.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), "licenses", safe_name + ".txt"), arcname='COPYING')

        if not meta_files_dir:
            prepare_meta_files(temp_dir)
            meta_files_dir = temp_dir
        add_meta_files(tar, meta_files_dir)
        shutil.rmtree(temp_dir)  # Cleanup

    return " + {location}/{archive_name}".format(location=location, archive_name=archive_name)


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
        import_data(os.path.join(temp_dir, 'cbdump', 'avg_rating'), 'avg_rating')
        import_data(os.path.join(temp_dir, 'cbdump', 'vote'), 'vote')

        # Reset sequence values after importing dump
        reset_sequence(['revision'])

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


def reset_sequence(table_names):
    connection = db.engine.raw_connection()
    try:
        cursor = connection.cursor()
        for table_name in table_names:
            cursor.execute(SQL("SELECT setval(pg_get_serial_sequence(%s, 'id'), coalesce(max(id),0) + 1, false) FROM {};")
                           .format(Identifier(table_name)), (table_name,))
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
