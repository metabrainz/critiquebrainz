from __future__ import with_statement
from fabric.api import *
from critiquebrainz import create_app


def extract_strings():
    """Extracts all strings into messages.pot."""
    local("pybabel extract -F critiquebrainz/babel.cfg -o messages.pot critiquebrainz")


def compile_translations():
    """Compiles existing translations for use."""
    local("pybabel compile -d critiquebrainz/translations")


def update_translations():
    """Pulls translations for languages defined in config from Transifex and compiles them."""
    languages = ','.join(create_app().config['SUPPORTED_LANGUAGES'])
    local("tx pull -f -r critiquebrainz.critiquebrainz -l %s" % languages)
    compile_translations()


def compile_styling():
    """Compiles styles.less into styles.css."""
    style_path = "critiquebrainz/static/css/"
    local("lessc --clean-css %sstyles.less > %sstyles.css" % (style_path, style_path))


def deploy():
    """Updates translations and compiles styling."""
    update_translations()
    compile_styling()
