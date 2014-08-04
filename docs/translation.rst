Client translation
==================

CritiqueBrainz uses `Transifex <https://www.transifex.com/>`_ to manage translations. If you want to contribute
translations, that's where you want to do it.

Working locally
---------------

Before doing anything make sure that you have virtual environment set up.
Activate it to have access to ``pybabel`` and ``fab`` commands::

   $ source ./env

Extracting strings
^^^^^^^^^^^^^^^^^^

To extract strings into a Portable Object Template use command::

   $ fab extract_strings

Adding new language
^^^^^^^^^^^^^^^^^^^

To add support for new language use::

   $ pybabel init -i messages.pot -d critiquebrainz/translations -l de

*Don't forget to replace 'de' with the language you need.*

After that you need to add new language into ``SUPPORTED_LANGUAGES`` list in default configuration file:
``default_config.py``.

Compiling translations
^^^^^^^^^^^^^^^^^^^^^^

To compile all created translation use::

   $ fab compile_translations

Updating translations
^^^^^^^^^^^^^^^^^^^^^

After modifying strings you'll probably want to update messages in different languages. To do this use::

   $ fab extract_strings
   $ pybabel update -i messages.pot -d critiquebrainz/translations

Afterwards some strings might be marked as fuzzy (where it tried to figure out if a translation matched a changed key).
If you have fuzzy entries, make sure to check them by hand and remove the fuzzy flag before compiling.

Additional info
^^^^^^^^^^^^^^^

CritiqueBrainz uses Flask-Babel extension. Its documentation is available at http://pythonhosted.org/Flask-Babel/.
