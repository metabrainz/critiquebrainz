Introduction
============

Setting up the server
---------------------

You can set up CritiqueBrainz server using `Docker <https://www.docker.com/>`_. It
requires minimum amount of configuration.

.. warning::
  Make sure you have the latest version of docker and docker-compose.

Configuration
^^^^^^^^^^^^^

First, you need to create custom configuration file. Copy the skeleton configuration::

   $ cp custom_config.py.example custom_config.py

Then open ``critiquebrainz/custom_config.py`` in your favourite text editor and update
configuration values as described next.

MusicBrainz login
'''''''''''''''''

To be able to log in using MusicBrainz accounts you need to set ``MUSICBRAINZ_CLIENT_ID``
and ``MUSICBRAINZ_CLIENT_SECRET`` OAuth values.

These values can be obtained from MusicBrainz after you register a new instance of
CritiqueBrainz at https://musicbrainz.org/account/applications/register (you'll need a
MusicBrainz account). In the ``Callback URL`` field type::

   http://<HOST>/login/musicbrainz/post

.. note::

   ``<HOST>`` field should be set to ``localhost`` if you plan to run a local instance of
   CritiqueBrainz for development purposes.
   For example:- If you are running your local instance of the server on Port Number
   8000 then ``<HOST>`` should be set
   to ``localhost:8000``.

After application has been registered, set ``MUSICBRAINZ_CLIENT_ID`` and ``MUSICBRAINZ_CLIENT_SECRET``
in your ``custom_config.py`` to the values that you see on the MusicBrainz website.

Spotfiy API authentication
''''''''''''''''''''''''''

To use the Spotify Web API, you need to set the ``SPOTIFY_CLIENT_ID`` and ``SPOTIFY_CLIENT_SECRET``
values. OAuth keys can be obtained after registering on the Spotify developer website.

After registering and logging into your Spotify account, head to
https://developer.spotify.com/my-applications/ and then register your application following the
instructions at https://developer.spotify.com/web-api/tutorial/#registering-your-application.

Finally, save the obtained ``Client ID`` and ``Client Secret`` fields in your ``custom_config.py``
fields ``SPOTIFY_CLIENT_ID`` and ``SPOTIFY_CLIENT_SECRET`` respectively.

Startup
^^^^^^^
Then you can build all the services::

   $ docker-compose -f docker/docker-compose.dev.yml build

MusicBrainz database containing all the MusicBrainz metadata is needed for
setting up your application. The ``mbdump.tar.bz2`` is the core MusicBrainz
archive which includes the tables for artist, release_group etc.
The ``mbdump-derived.tar.bz2`` archive contains annotations, user tags and search indexes.
These archives include all the data required for setting up an instance of
CritiqueBrainz.

One can import the database dump by downloading and importing the data in
a single command::

    $ docker-compose -f docker/docker-compose.dev.yml run musicbrainz_db

.. note::

  One can also manually download the dumps and then import it:-

  i. For this, you have to download the dumps ``mbdump.tar.bz2`` and ``mbdump-derived.tar.bz2``
     from http://ftp.musicbrainz.org/pub/musicbrainz/data/fullexport/.

     .. warning::

        Make sure to get the latest dumps

  ii. Then the environment variable ``DUMPS_DIR`` must be set to the path of the
      folders containing the dumps. This can be done by::

        $ export DUMPS_DIR="Path of the folder containing the dumps"

      You can check that the variable ``DUMPS_DIR`` has been succesfully assigned or not by::

        $ echo $DUMPS_DIR

      This must display the path of your folder containing database dumps. The folder must contain at least
      the file ``mbdump.tar.bz2``.

  iii. Then import the database dumps by this command::

        $ docker-compose -f docker/docker-compose.dev.yml run -v $DUMPS_DIR:/home/musicbrainz/dumps \
        -v $PWD/data/mbdata:/var/lib/postgresql/data/pgdata musicbrainz_db

.. note::
  You can also use the smaller sample dumps available at http://ftp.musicbrainz.org/pub/musicbrainz/data/sample/
  to set up the MusicBrainz database. However, note that these dumps are .tar.xz
  dumps while CritiqueBrainz currently only supports import of .tar.bz2 dumps.
  So, a decompression of the sample dumps and recompression into .tar.bz2 dumps
  will be needed. This can be done using the following command

      $ xzcat mbdump-sample.tar.xz | bzip2 > mbdump.tar.bz2


.. warning::

   Keep in mind that this process is very time consuming, so make sure that you don't delete
   the ``data/mbdata`` directory by accident. Also make sure that you have about 25GB of free
   space to keep the MusicBrainz data.

Initialization of CritiqueBrainz database is also required::

   $ docker-compose -f docker/docker-compose.dev.yml run critiquebrainz python3 \
   manage.py init_db --skip-create-db

Then you can start all the services::

   $ docker-compose -f docker/docker-compose.dev.yml up -d

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

   $ docker-compose -f docker/docker-compose.test.yml up --build

Modifying strings
-----------------

CritiqueBrainz supports interface translation. If you add or modify strings that will be displayed
to users, then you need to wrap them in one of two functions: ``gettext()`` or ``ngettext()``.

Before committing changes don't forget to extract all strings into ``messages.pot``::

   $ python3 manage.py update_strings

For more info see :doc:`translation`.
