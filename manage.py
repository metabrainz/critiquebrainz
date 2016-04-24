from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from critiquebrainz import frontend
from critiquebrainz import ws
from critiquebrainz import cache
from critiquebrainz.data import dump_manager
import critiquebrainz.data.utils as data_utils
import critiquebrainz.data.fixtures as _fixtures
import subprocess
import click


cli = click.Group()

application = DispatcherMiddleware(frontend.create_app(), {
    "/ws/1": ws.create_app()
})

OBSERVE_FILES = [
    "critiquebrainz/frontend/static/build/rev-manifest.json",
]


@cli.command()
@click.option("--host", "-h", default="0.0.0.0", show_default=True)
@click.option("--port", "-p", default=8080, show_default=True)
@click.option("--debug", "-d", is_flag=True,
              help="Turns debugging mode on or off. If specified, overrides "
                   "'DEBUG' value in the config file.")
def runserver(host, port, debug=False):
    run_simple(host, port, application, use_debugger=debug,
               extra_files=OBSERVE_FILES)


@cli.command()
def extract_strings():
    """Extract all strings into messages.pot.

    This command should be run after any translatable strings are updated.
    Otherwise updates are not going to be available on Transifex.
    """
    _run_command("pybabel extract -F critiquebrainz/frontend/babel.cfg -k lazy_gettext "
                 "-o critiquebrainz/frontend/messages.pot critiquebrainz/frontend")
    click.echo("Strings have been successfully extracted into messages.pot file.")


@cli.command()
def pull_translations():
    """Pull translations for languages defined in config from Transifex and compile them.

    Before using this command make sure that you properly configured Transifex client.
    More info about that is available at http://docs.transifex.com/developer/client/setup#configuration.
    """
    languages = ','.join(frontend.create_app().config['SUPPORTED_LANGUAGES'])
    _run_command("tx pull -f -r critiquebrainz.critiquebrainz -l %s" % languages)


@cli.command()
def update_strings():
    """Extract strings and pull translations from Transifex."""
    extract_strings()
    pull_translations()


@cli.command()
def compile_translations():
    """Compile translations for use."""
    _run_command("pybabel compile -d critiquebrainz/frontend/translations")
    click.echo("Translated strings have been compiled and ready to be used.")


@cli.command()
def clear_memcached():
    with frontend.create_app().app_context():
        cache.flush_all()
    click.echo("Flushed everything from memcached.")


@cli.command()
def init_db():
    """Initialize the database.

    * Creates the database.
    * Creates all tables.
    * Adds fixtures required to run the app.
    """
    click.echo("Initializing the database...")

    init_postgres(frontend.create_app().config['SQLALCHEMY_DATABASE_URI'])

    click.echo("Creating tables... ", nl=False)
    data_utils.create_tables(frontend.create_app())
    click.echo("Done!")

    click.echo("Adding fixtures... ")
    app = frontend.create_app()
    with app.app_context():
        _fixtures.install(app, *_fixtures.all_data)
    click.echo("Done!")

    click.echo("Initialization has been completed!")


@cli.command()
def init_test_db():
    """Initialize the database.

    * Creates the database.
    * Creates all tables.
    * Adds fixtures required to run the app.
    """
    click.echo("Initializing the database for testing...")
    init_postgres(frontend.create_app().config['TEST_SQLALCHEMY_DATABASE_URI'])
    click.echo("Initialization has been completed!")


def init_postgres(db_uri):
    """Initializes PostgreSQL database from provided URI.

    New user and database will be created, if needed. It also creates uuid-ossp extension.
    """
    hostname, db, username, password = data_utils.explode_db_uri(db_uri)
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


def _run_command(command):
    return subprocess.check_call(command, shell=True)


cli.add_command(dump_manager.cli, name="dump")


if __name__ == '__main__':
    cli()
