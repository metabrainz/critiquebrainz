Installation
============

Requirements
------------

* Python (tested on 2.7.4)
* ``python-dev``
* PostgreSQL (tested on 9.1.9)
* ``postgresql-contrib``
* ``postgresql-server-dev-9.1``
* virtualenv
* memcached

How to start
------------

Creating virtualenv (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This step is not required, but highly recommended for development instances.
You may find it useful to keep libraries needed by CritiqueBrainz seperated
from your global python libraries. To achieve this, you will need a
``virtualenv`` package. You may install it with ``pip`` or ``apt-get`` on Debian/Ubuntu
systems::

   $ sudo pip install virtualenv (or)
   $ sudo apt-get install python-virtualenv

Then run::

   $ scripts/virtualenv.sh

It will create a symbolic link ``env`` to virtualenv's entry point in your
``critiquebrainz/`` directory. To enter newly created virtualenv, type in::

   $ source ./env

You should do this before executing any other file from CritiqueBrainz package.

Installing dependencies
^^^^^^^^^^^^^^^^^^^^^^^

If you're in your desired python environment, simply run::

   $ pip install -r requirements.txt

to install all required dependencies.

Configuration
^^^^^^^^^^^^^

First, you need to create custom configuration file. Copy the skeleton configuration::

   $ cp critiquebrainz/config.py.example critiquebrainz/config.py

Then, open ``critiquebrainz/config.py`` in your favourite text editor, uncomment
``SQLALCHEMY_DATABASE_URI`` variable, and fill in the fields in angle brackets.

Now, you need to create and configure the database with::

   $ python manage.py data create_db

This command will

* create new PostgreSQL role, if needed
* create new PostgreSQL database, if needed
* register ``uuid-ossp`` PostgreSQL extension, if needed

You also need to update the newly created database with default schema
and testing data. To do this type::

   $ python manage.py data fixtures

Preparing login
^^^^^^^^^^^^^^^

Before you begin using authentication with MusicBrainz accounts,
you need to set ``MUSICBRAINZ_CLIENT_ID`` and ``MUSICBRAINZ_CLIENT_SECRET`` in
``critiquebrainz/config.py``. To obtain these keys, you need to register your
instance of CrituqeBrainz on MusicBrainz.

**Note** ``<your domain>`` field in the urls listed below should probably be set
to ``127.0.0.1:5000``, if you plan to run your CritiqueBrainz instance locally
in development mode.

MusicBrainz
"""""""""""

You need MusicBrainz account to register your application. Then head to
https://musicbrainz.org/account/applications/register and follow the instructions.
In ``Callback URL`` field type::

   http://<your domain>/login/musicbrainz/post

Finally, save the obtained ``OAuth Client ID`` and ``OAuth Client Secret`` fields
in your ``config.py`` fields ``MUSICBRAINZ_CLIENT_ID`` and ``MUSICBRAINZ_CLIENT_SECRET``
respectively.

Security
^^^^^^^^

Unless you are doing development, it might be a good idea to make your installation
HTTPS-only. You can read about pros and cons at https://security.stackexchange.com/questions/258/.
If you don't want to do that yet, here's a list of blueprints that should be kept secure:

* ``profile_details`` (private user info)
* ``profile_applications`` (secret info about user's applications)
* ``ws_oauth`` (OAuth 2.0 token endpoint)

More information about importance of keeping transport layer secure is available at
https://www.owasp.org/index.php/Top_10_2010-A9-Insufficient_Transport_Layer_Protection.

Running the server
------------------

   $ python run.py
