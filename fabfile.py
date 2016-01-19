from __future__ import with_statement
from fabric.api import local
from fabric.colors import green, yellow
from critiquebrainz.frontend import create_app
from critiquebrainz import cache
from manage import init_postgres


def extract_strings():
    """Extract all strings into messages.pot.

    This command should be run after any translatable strings are updated.
    Otherwise updates are not going to be available on Transifex.
    """
    local("pybabel extract -F critiquebrainz/frontend/babel.cfg -k lazy_gettext -o critiquebrainz/frontend/messages.pot critiquebrainz/frontend")
    print(green("Strings have been successfully extracted into messages.pot file.", bold=True))


def pull_translations():
    """Pull translations for languages defined in config from Transifex and compile them.

    Before using this command make sure that you properly configured Transifex client.
    More info about that is available at http://docs.transifex.com/developer/client/setup#configuration.
    """
    languages = ','.join(create_app().config['SUPPORTED_LANGUAGES'])
    local("tx pull -f -r critiquebrainz.critiquebrainz -l %s" % languages)
    print(green("Translations have been updated successfully.", bold=True))


def update_strings():
    """Extract strings and pull translations from Transifex."""
    extract_strings()
    pull_translations()


def compile_translations():
    """Compile translations for use."""
    local("pybabel compile -d critiquebrainz/frontend/translations")
    print(green("Translated strings have been compiled and ready to be used.", bold=True))


def compile_styling():
    """Compile styles.less into styles.css.

    This command requires Less (CSS pre-processor). More information about it can be
    found at http://lesscss.org/.
    """
    style_path = "critiquebrainz/frontend/static/css/"
    local("lessc --clean-css %smain.less > %smain.css" % (style_path, style_path))
    print(green("Style sheets have been compiled successfully.", bold=True))


def clear_memcached():
    with create_app().app_context():
        cache.flush_all()
    print(green("Flushed everything from memcached.", bold=True))


def git_pull():
    local("git pull origin")
    print(green("Updated local code.", bold=True))


def deploy():
    git_pull()
    compile_translations()
    compile_styling()
    clear_memcached()


def test(init_db=True, coverage=True):
    """Run all tests.

    It will also initialize the test database and create code coverage report, unless
    specified otherwise. Database that will be used for tests can be specified in the
    application config file. See `TEST_SQLALCHEMY_DATABASE_URI` variable.

    Code coverage report will be located in cover/index.html file.
    """
    if init_db:
        # Creating database-related stuff
        init_postgres(create_app().config['TEST_SQLALCHEMY_DATABASE_URI'])

    if coverage:
        local("nosetests --exe --with-coverage --cover-package=critiquebrainz --cover-erase --cover-html")
        print(yellow("Coverage report can be found in cover/index.html file.", bold=True))
    else:
        local("nosetests --exe")
