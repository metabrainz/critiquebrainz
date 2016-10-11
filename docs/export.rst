Exporting data
==============

You can create backups including various pieces of data that we store: reviews,
revisions, users, and other stuff. Some parts include private data about users
that is not meant to be shared.

Creating data dumps
-------------------

Below you can find commands that can be used to create backups of different formats.

Complete database dump *(for PostgreSQL)*::

   $ docker-compose run web python3 manage.py dump full_db

MusicBrainz-style dump public *(no private info)*::

   $ docker-compose run web python3 manage.py dump public

JSON dump with all reviews *(no private info)*::

   $ docker-compose run web python3 manage.py dump json

All commands have rotation feature which can be enabled by passing `-r` argument.
