from __future__ import with_statement
from fabric.api import local
from critiquebrainz.frontend import create_app


def extract_strings():
    """Extract all strings into messages.pot."""
    local("pybabel extract -F critiquebrainz/frontend/babel.cfg -k lazy_gettext -o messages.pot critiquebrainz/frontend")


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
    local("lessc --clean-css %sstyles.less > %sstyles.css" % (style_path, style_path))
    print(green("Style sheets have been compiled successfully.", bold=True))


def deploy():
    """Compile translations and styling."""
    compile_translations()
    compile_styling()
