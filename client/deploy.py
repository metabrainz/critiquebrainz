# !/usr/bin/python
import subprocess
import critiquebrainz.config as conf


def compile_styling():
    print "Compiling styles..."
    style_path = "critiquebrainz/static/css/"
    exit_code = subprocess.call("lessc --clean-css %sstyles.less > %sstyles.css" % (style_path, style_path), shell=True)
    if exit_code != 0:
        raise Exception("Failed to compile styles!")
    print "Done."


def update_translations():
    print "Extracting strings..."
    exit_code = subprocess.call("pybabel extract -F critiquebrainz/babel.cfg -o messages.pot critiquebrainz", shell=True)
    if exit_code != 0:
        raise Exception("Failed to extract strings!")
    print "Done."

    print "Updating translations..."
    languages = ','.join(conf.LANGUAGES.keys())
    print "tx pull -a -l %s" % languages
    exit_code = subprocess.call("tx pull -r critiquebrainz.critiquebrainz -l %s" % languages, shell=True)
    if exit_code != 0:
        raise Exception("Failed to update translations!")
    print "Done."

    print "Compiling translations..."
    exit_code = subprocess.call("pybabel compile -d critiquebrainz/translations", shell=True)
    if exit_code != 0:
        raise Exception("Failed to compile translations!")
    print "Done."


if __name__ == '__main__':
    compile_styling()
    update_translations()