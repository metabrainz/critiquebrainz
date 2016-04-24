Translation
===========

Our goal is to make CritiqueBrainz project accessible to readers and writers
all over the world. You can post reviews in any language you want, but it is
also important to provide good way to find these reviews.
That's why we need your help!

Translation process is being done on `Transifex <https://www.transifex.com/>`_
platform. You can submit your translation suggestions there and collaborate
with other translators. If you want to contribute translations, that's where
you should to do it.

Our project page is located at https://www.transifex.com/projects/p/critiquebrainz/.

There are a couple of things you should know if you are trying to modify strings.
See the info below.

Extracting strings
------------------

To extract strings into a Portable Object Template file (*messages.pot*) use command::

   $ python3 manage.py extract_strings

Adding support for a new language
---------------------------------

To add support for new language add its Transifex code into ``SUPPORTED_LANGUAGES``
list in default configuration file: ``default_config.py``. After that you can pull
translations from Transifex::

   $ python3 manage.py  pull_translations

You will need to create *.transifexrc* file that will look like::

   [https://www.transifex.com]
   hostname = https://www.transifex.com
   username = <YOUR_EMAIL>
   password = <YOUR_PASSWORD>
   token =

More info about setup process is available at http://docs.transifex.com/developer/client/setup.

Additional info
---------------

CritiqueBrainz uses Flask-Babel extension. Its documentation is available at
http://pythonhosted.org/Flask-Babel/.
