Backups
=======

You can create backups including various pieces of data that we store: reviews,
revisions, users, and other stuff. Some parts include private data about users
that is not meant to be shared.

Creating backups
----------------

Below you can find commands that can be used to create backups of different formats.

Complete database dump *(for PostgreSQL)*::

   $ python manage.py data backup dump_db -r

JSON dump with all reviews *(no private info)*::

   $ python manage.py data backup dump_json -r

MusicBrainz-style dump *(no private info)*::

   $ python manage.py data backup export -r
