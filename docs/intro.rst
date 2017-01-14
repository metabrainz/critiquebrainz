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

Then you can start all the services::

   $ docker-compose -f docker/docker-compose.dev.yml up -d --build

The first time you do that, database initialization is also required::

   $ docker-compose -f docker/docker-compose.dev.yml run critiquebrainz python3 manage.py init_db --skip-create-db

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
