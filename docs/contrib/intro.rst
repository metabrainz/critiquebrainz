Introduction
============

CritiqueBrainz project is separated into three main packages: data, frontend, and web service (ws).
The data package is used to interact with the database. The frontend provides user-friendly interface
that is available at https://critiquebrainz.org. The web service provides web API for CritiqueBrainz
(see :doc:`../dev/api`).

*Here's an overview of the project structure:*

.. image:: /images/structure.svg

Contributing
^^^^^^^^^^^^

See `CONTRIBUTING.md file <https://github.com/metabrainz/critiquebrainz/blob/master/CONTRIBUTING.md>`_.

Using Vagrant
^^^^^^^^^^^^^

Vagrant significantly simplifies development process on all major platforms by running applications in
reproducible environment. It is available at http://www.vagrantup.com/.

You can use it for CritiqueBrainz development. All you need to do is set up custom configuration file.
After that you can start a VM and connect to it::

   $ vagrant up
   $ vagrant ssh

After VM is created and running, you can start the application::

    $ cd /vagrant
    $ python manage.py runserver -d

Web server should be accessible at http://localhost:8080/.

PostgreSQL will also be available on port *15432* with `trust`_ authentication method.

.. _trust: http://www.postgresql.org/docs/9.1/static/auth-methods.html#AUTH-TRUST

Testing
^^^^^^^

To run all tests use::

   $ fab test

This command run all tests and, if successful, produce a test coverage report.

Modifying strings
^^^^^^^^^^^^^^^^^

CritiqueBrainz supports interface translation. If you add or modify strings that will be displayed
to users, then you need to wrap them in one of two functions: ``gettext()`` or ``ngettext()``.

Before committing changes don't forget to extract all strings into ``messages.pot``:

   $ fab update_strings

For more info see :doc:`translation`.
