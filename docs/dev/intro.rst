Introduction
============

CritiqueBrainz project is separated into three main packages: data, frontend, and web service (ws).
The data package is used to interact with the database. The frontend provides user-friendly interface
that is available at https://critiquebrainz.org. The web service provides web API for CritiqueBrainz
(see :doc:`api`).

Contributing
^^^^^^^^^^^^

See `CONTRIBUTING.md file <https://github.com/metabrainz/critiquebrainz/blob/master/CONTRIBUTING.md>`_.

Using Vagrant
^^^^^^^^^^^^^

Vagrant significantly simplifies development process on all major platforms by running applications in reproducible
environment. It is available at http://www.vagrantup.com/.

You can use it for CritiqueBrainz development. All you need to do is set up custom configuration file.
After that you can start a VM and connect to it::

   $ vagrant up
   $ vagrant ssh

After starting a VM you should be able to access server at ``http://127.0.0.1:5000/``.
PostgreSQL will be available on port *15432* with `trust`_ authentication method.

.. _trust: http://www.postgresql.org/docs/9.1/static/auth-methods.html#AUTH-TRUST

Server will be running in a separate `screen <https://www.gnu.org/software/screen/>`_.
You can connect to it to see standard output, do maintenance or other tasks.

Modifying strings
^^^^^^^^^^^^^^^^^

CritiqueBrainz supports interface translation. If you add or modify strings that will be displayed to user,
then you need to wrap them in one of two functions: ``gettext()`` or ``ngettext()``.

Before committing changes don't forget to extract all strings into ``messages.pot``.

For more info see :doc:`../translation`.
