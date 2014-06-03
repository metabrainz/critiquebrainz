Client translation
==================

Before doing anything make sure that you have client's virtual environment set up.
Activate it to have access to ``pybabel`` command::

    $ source ./env

Extracting strings
------------------

To extract strings into a Portable Object Template use ``pybabel extract`` command::

    $ pybabel extract -F critiquebrainz/babel.cfg -o messages.pot critiquebrainz

Adding new language
-------------------

To add support for new language use::

    $ pybabel init -i messages.pot -d critiquebrainz/translations -l de

*Don't forget to replace 'de' with the language you need.*

After that you need to add new language into ``LANGUAGES`` variable in client's ``config.py``.

Compiling translations
----------------------

To compile all created translation use::

    $ pybabel compile -d critiquebrainz/translations

Updating translations
---------------------

After modifying strings you'll probably want to update messages in different languages. To do this use::

    $ pybabel extract -F critiquebrainz/babel.cfg -o messages.pot critiquebrainz
    $ pybabel update -i messages.pot -d critiquebrainz/translations

Afterwards some strings might be marked as fuzzy (where it tried to figure out if a translation matched a changed key).
If you have fuzzy entries, make sure to check them by hand and remove the fuzzy flag before compiling.

Additional info
---------------

CritiqueBrainz uses Flask-Babel extension. Its documentation is available at http://pythonhosted.org/Flask-Babel/.