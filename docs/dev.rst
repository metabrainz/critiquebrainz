Development
===========

Using Vagrant
-------------

Vagrant significantly simplifies development process on all major platforms by running applications in reproducible
environment. It is available at http://www.vagrantup.com/.

You can use it for CritiqueBrainz development. All you need to do is set up configuration files for server and client.
After that you can start a VM and connect to it::

   $ vagrant up
   $ vagrant ssh

To run a server use::

   $ python manage.py runserver -t 0.0.0.0 -p 5000

and to run a client::

   $ python manage.py runserver -t 0.0.0.0 -p 5001

`It might be a good idea to use something like GNU Screen to be able to run both at the same time.`

After activating server and client you should be able to access both on ``http://127.0.0.1:5001/`` (client)
and ``http://127.0.0.1:5000/`` (server). PostgreSQL will be available on port 5433.

Modifying strings in client
---------------------------

CritiqueBrainz Client supports interface translation. If you add or modify strings that will be displayed to user,
you need to wrap them in one of two functions: ``gettext()`` or ``ngettext()``.

Before committing changes don't forget to extract all strings into ``messages.pot``.

For more info see :doc:`translation`.
