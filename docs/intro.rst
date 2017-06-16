Introduction
============

Setting up the server
---------------------

You can set up CritiqueBrainz server using `Docker <https://www.docker.com/>`_. It
requires minimum amount of configuration.

Configuration
^^^^^^^^^^^^^

First, you need to create custom configuration file. Copy the skeleton configuration::

   $ cp custom_config.py.example custom_config.py

Then, open ``critiquebrainz/config.py`` in your favourite text editor and update
any variables, as needed.

Configuring MusicBrainz login
'''''''''''''''''''''''''''''

Before you begin using authentication with MusicBrainz accounts,
you need to set ``MUSICBRAINZ_CLIENT_ID`` and ``MUSICBRAINZ_CLIENT_SECRET`` values.
To obtain these keys, you need to register your instance of CrituqeBrainz on MusicBrainz.

**Note** ``<your domain>`` field in the urls listed below should probably be set
to ``localhost``, if you plan to run your CritiqueBrainz instance locally
in development mode.

You need MusicBrainz account to register your application. Then head to
https://musicbrainz.org/account/applications/register and follow the instructions.
In ``Callback URL`` field type::

   http://<your domain>/login/musicbrainz/post

Finally, save the obtained ``OAuth Client ID`` and ``OAuth Client Secret`` fields
in your ``config.py`` fields ``MUSICBRAINZ_CLIENT_ID`` and ``MUSICBRAINZ_CLIENT_SECRET``
respectively.

Startup
^^^^^^^
Then you can build all the services::

   $ docker-compose -f docker/docker-compose.dev.yml build

You need MusicBrainz database containing all the MusicBrainz music metadata for setting up your application. Data dumps provided from https://musicbrainz.org can be downloaded from https://musicbrainz.org/doc/MusicBrainz_Database/Download. ``mbdump.tar.bz2`` is the core MusicBrainz database including the tables for artist, release groups etc. ``mbdump-derived.tar.bz2`` contains annotations, user tags and search indexes. The core and the derived database covers almost all the data required for a CritiqueBrainz server.

Then you can create and populate the database::

   $ docker-compose -f docker/docker-compose.dev.yml run -v $DUMPS_DIR:/home/musicbrainz/musicbrainz-server -v $PWD/data/mbdata:/var/lib/postgresql/data/pgdata musicbrainz_db

**Note** ``DUMP_DIR`` should be set to the path containing the downloaded dumps.

You can skip downloading the dumps separately. Get the dumps, create and populate the database using::

   $ docker-compose -f docker/docker-compose.dev.yml run -v $PWD/data/mbdata:/var/lib/postgresql/data/pgdata musicbrainz_db

**Note** The above command downloads only the latest ``mbdump.tar.bz2`` and ``mbdump-derived.tar.bz2`` dumps for populating the database.

Initialization of CritiqueBrainz database is also required::

   $ docker-compose -f docker/docker-compose.dev.yml run critiquebrainz python3 manage.py init_db --skip-create-db

Then you can start all the services::

   $ docker-compose -f docker/docker-compose.dev.yml up -d

**Note** Alternative way to build, download and import dumps for MusicBrainz database and run all services::

   $ docker-compose -f docker/docker-compose.dev.yml up -d --build

This will set up the MusicBrainz database by downloading the dumps. The first time after this is run, initialization of CritiqueBrainz database is also required.

Building static files
'''''''''''''''''''''

Current Docker setup for development has one caveat: installation of Node.js dependencies
and static file builds need to be done manually. This is caused by the volume setup.

After you started development versions of containers with Compose, connect to the main
container::

   $ docker-compose -f docker/docker-compose.dev.yml run critiquebrainz /bin/bash

then install dependencies (it's enough to do this once, unless you modify ``package.json``)
and build static files (needs to be done after any changes to JS or Less)::

   root@<container_id>:/code# npm install
   root@<container_id>:/code# ./node_modules/.bin/gulp

Importing data dump
'''''''''''''''''''

We provide daily data dumps from https://critiquebrainz.org that include reviews
and most of the data associated with them. If you want to import that into your
own installation, download archives from ftp://ftp.musicbrainz.org/pub/musicbrainz/critiquebrainz/dump/
(you'll need to get the base archive ``cbdump.tar.bz2`` and one with reviews)
and use ``python3 manage.py export importer`` command. First you need to import
base archive and then one that contains reviews. For example::

   $ docker-compose -f docker/docker-compose.dev.yml run critiquebrainz python3 manage.py dump import cbdump.tar.bz2
   $ docker-compose -f docker/docker-compose.dev.yml run critiquebrainz python3 manage.py dump import cbdump-reviews-all.tar.bz2

Keep in mind that CritiqueBrainz only supports importing into an empty database.
This should work if you just ran ``init_db`` command.


Testing
-------

Alternative way to test the web server is to use a Docker container::

   $ docker-compose -f docker/docker-compose.test.yml up -d --build
   $ docker logs -f critiquebrainz_web_test_1

Modifying strings
-----------------

CritiqueBrainz supports interface translation. If you add or modify strings that will be displayed
to users, then you need to wrap them in one of two functions: ``gettext()`` or ``ngettext()``.

Before committing changes don't forget to extract all strings into ``messages.pot``::

   $ python3 manage.py update_strings

For more info see :doc:`translation`.
