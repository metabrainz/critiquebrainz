Installation
============

Requirements
------------

* Python 3.4
* ``python3-dev``
* PostgreSQL (tested on 9.3)
* ``postgresql-contrib``
* ``postgresql-server-dev-9.3``
* nodejs (tested on 4.4.3)
* virtualenv
* memcached
* git

How to start
------------

Creating virtualenv (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This step is not required, but highly recommended! You may find it useful
to keep libraries needed by CritiqueBrainz separated from your global Python
libraries. To achieve this, you will need a ``virtualenv`` package. You may
install it with ``pip`` or ``apt-get`` on Debian/Ubuntu systems::

   $ sudo pip3 install virtualenv

or::

   $ sudo apt-get install python3-virtualenv

Then run to create a virtual environment::

   $ virtualenv venv

To enter newly created virtualenv, type in::

   $ . venv/bin/activate

You should do this before executing any other file from CritiqueBrainz package.

Configuration
^^^^^^^^^^^^^

First, you need to create custom configuration file. Copy the skeleton configuration::

   $ cp critiquebrainz/config.py.example critiquebrainz/config.py

Then, open ``critiquebrainz/config.py`` in your favourite text editor and update
any variables, as needed.

Configuring MusicBrainz login
"""""""""""""""""""""""""""""

Before you begin using authentication with MusicBrainz accounts,
you need to set ``MUSICBRAINZ_CLIENT_ID`` and ``MUSICBRAINZ_CLIENT_SECRET`` in
``critiquebrainz/config.py``. To obtain these keys, you need to register your
instance of CrituqeBrainz on MusicBrainz.

**Note** ``<your domain>`` field in the urls listed below should probably be set
to ``127.0.0.1:8080``, if you plan to run your CritiqueBrainz instance locally
in development mode.

You need MusicBrainz account to register your application. Then head to
https://musicbrainz.org/account/applications/register and follow the instructions.
In ``Callback URL`` field type::

   http://<your domain>/login/musicbrainz/post

Finally, save the obtained ``OAuth Client ID`` and ``OAuth Client Secret`` fields
in your ``config.py`` fields ``MUSICBRAINZ_CLIENT_ID`` and ``MUSICBRAINZ_CLIENT_SECRET``
respectively.

Installing dependencies
^^^^^^^^^^^^^^^^^^^^^^^

If you're in your desired Python environment, simply run::

   $ pip3 install -r requirements.txt

to install all required dependencies.

Database initialization
^^^^^^^^^^^^^^^^^^^^^^^

Now, you need to create and configure the database with::

   $ python3 manage.py init_db

This command will

* create new PostgreSQL role, if needed
* create new PostgreSQL database, if needed
* register ``uuid-ossp`` PostgreSQL extension, if needed
* add fixtures

Importing data
""""""""""""""

We provide daily data dumps from https://critiquebrainz.org that include reviews
and most of the data associated with them. If you want to import that into your
own installation, download archives from ftp://ftp.musicbrainz.org/pub/musicbrainz/critiquebrainz/dump/
(you'll need to get the base archive ``cbdump.tar.bz2`` and one with reviews)
and use ``python3 manage.py export importer`` command. First you need to import
base archive and then one that contains reviews. For example::

   $ python3 manage.py dump import cbdump.tar.bz2
   $ python3 manage.py dump import cbdump-reviews-all.tar.bz2

Keep in mind that CritiqueBrainz only supports importing into an empty database.

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

Building static files
^^^^^^^^^^^^^^^^^^^^^

Static files in CritiqueBrainz need to built before use. This is done using Node.js.
To install it run::

   $ curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -
   $ sudo apt-get install -y nodejs

Once node is installed, you can install all the dependencies::

   $ npm install

Now, to actually run the build do::

   $ ./admin/compile_resources.sh

Running the server
------------------

To run the server you can use ``manage.py`` script::

   $ python3 manage.py runserver -d
