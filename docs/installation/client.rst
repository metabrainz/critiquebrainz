Client Installation
===================

Requirements
------------

* Python (tested on 2.7.4)
* virtualenv
* memcached

How to start
------------

Creating virtualenv (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This step is not required, but highly recommended for development instances.
You may find it useful to keep libraries needed by CritiqueBrainz seperated
from your global python libraries. To achieve this, you will need a
``virtualenv`` package. You may install it with ``pip`` or ``apt-get`` on Debian/Ubuntu
systems::

    $ sudo pip install virtualenv # (or)
    $ sudo apt-get install python-virtualenv

Then run::

    $ scripts/virtualenv.sh

It will create a symbolic link ``env`` to virtualenv's entry point in your
``critiquebrainz/`` directory. To enter newly created virtualenv, type in::

    $ source ./env

You should do this before executing any other file from CritiqueBrainz package.

Installing dependencies
^^^^^^^^^^^^^^^^^^^^^^^

If you're in your desired python environment, simply run::

    $ pip install -r requirements.txt

Configuring
^^^^^^^^^^^

Start with copying the example config file::

    $ cp critiquebrainz/config.py.example critiquebrainz/config.py

Then, set your ``CRITIQUEBRAINZ_CLIENT_ID`` and ``CRITIQUEBRAINZ_CLIENT_SECRET``
to an existing ``critiquebrainz-server`` client with an ``authorization`` scope.
You may keep the defaults, if you want to use the default client from
``critiquebrainz-server`` fixtures. It assumes your ``critiquebrainz-server``
instance is listening on ``127.0.0.1:5000``. If you want to change it, you
should edit this OAuth client in your database manually (as of now).


Preparing to run
^^^^^^^^^^^^^^^^

Before you start client you need to compile styles and pull translations. This can be done using deployment script::

    $ python deploy.py

`Note:` You need to set up Transifex before updating translation. For more info see http://docs.transifex.com/developer/client/.

Running
-------

Don't forget to enter your virtual environment first::

    $ source ./env

Now you can safely run the webservice app::

    $ ./run.sh

