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

After VM is created and running you can build static files (this needs to be done if you make changes
to JavaScript or Less files)::

   $ cd /vagrant
   $ ./admin/compile_resources.sh

Then you can start the application::

   $ cd /vagrant
   $ python3 manage.py runserver -d

Web server should be accessible at http://localhost:8080/.

PostgreSQL will also be available on port *15432* with `trust`_ authentication method.

.. _trust: http://www.postgresql.org/docs/9.1/static/auth-methods.html#AUTH-TRUST

Using Docker
^^^^^^^^^^^^

Instead of Vagrant you can also use Docker container that comes with CritiqueBrainz. It requires minimum amount of
configuration.

First, copy configuration file on your workstation and make all the necessary modifications::

   $ cd critiquebrainz
   $ cp config.py.example config.py

Then you can start all the services::

   $ docker-compose up -d

The first time you do that, database initialization is also required::

   $ docker-compose run web python3 manage.py init_db --skip-create-db

Testing
^^^^^^^

To run all tests use::

   $ py.test critiquebrainz/

This command run all tests and, if successful, produce a test coverage report.

Testing with Docker
^^^^^^^^^^^^^^^^^^

Alternative way to test the web server is to use a Docker container::

   $ docker-compose -f docker-compose.test.yml build
   $ docker-compose -f docker-compose.test.yml up -d
   $ docker logs -f critiquebrainz_web_test_1

Modifying strings
^^^^^^^^^^^^^^^^^

CritiqueBrainz supports interface translation. If you add or modify strings that will be displayed
to users, then you need to wrap them in one of two functions: ``gettext()`` or ``ngettext()``.

Before committing changes don't forget to extract all strings into ``messages.pot``:

   $ python3 manage.py update_strings

For more info see :doc:`translation`.
