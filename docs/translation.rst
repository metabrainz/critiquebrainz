Client translation
==================

CritiqueBrainz uses `Transifex <https://www.transifex.com/>`_ to manage translations.
Project homepage is located at https://www.transifex.com/projects/p/critiquebrainz/.
If you want to contribute translations, that's where you should to do it.

Working locally
---------------

Before doing anything make sure that you have virtual environment set up.
Activate it to have access to ``pybabel`` and ``fab`` commands::

   $ source ./env

Extracting strings
^^^^^^^^^^^^^^^^^^

To extract strings into a Portable Object Template file (*messages.pot*) use command::

   $ fab extract_strings

Adding support for a new language
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add support for new language add its Transifex code into ``SUPPORTED_LANGUAGES`` list in default configuration file:
``default_config.py``. After that you can pull translations from Transifex::

   $ fab pull_translations

You will need to create *.transifexrc* file that will look like::

   [https://www.transifex.com]
   hostname = https://www.transifex.com
   username = <YOUR_EMAIL>
   password = <YOUR_PASSWORD>
   token =

More info about setup process is available at http://docs.transifex.com/developer/client/setup.

Additional info
^^^^^^^^^^^^^^^

CritiqueBrainz uses Flask-Babel extension. Its documentation is available at http://pythonhosted.org/Flask-Babel/.
