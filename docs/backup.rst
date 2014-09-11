Backups
=======

Don't forget to enter your virtual environment first::

   $ source ./env

Creating backups
----------------

Complete database dump::

   $ python manage.py data backup backup_db -r

JSON dump with all reviews *(no private info)*::

   $ python manage.py data backup dump_json -r

MusicBrainz-style dump *(no private info)*::

   $ python manage.py data backup export -r
