critiquebrainz
==============

A GSoC project for MetaBrainz Foundation. 

##Requirements

* PostgreSQL (tested on 9.1.9)
* Python (tested on 2.7.4)
* virtualenv

##Getting critiquebrainz

To get an instance of critiquebrainz server, simply clone the master branch

    git clone https://github.com/mjjc/critiquebrainz.git

##Preparing database

First, you need to create a database on your PostgreSQL server. Then enter
your critiquebrainz directory and create a configuration from a template

    cp critiquebrainz/config.py.example critiquebrainz/config.py

and open `critiquebrainz/config.py` in your favourite text editor. Now fill the
`SQLALCHEMY_DATABASE_URI` with your database configuration.

*Notice* In order to run the tests, you need to create a second database with
`_test` suffix.

##Configuring environment

First, you need to create and setup a new python environment.

    cd critiquebrainz-master (your repository directory)
    virtualenv venv
    . venv/bin/activate
    python setup.py install

This will install all necessary python packages to your new virtual environment.

##Running

Remeber to enter your virtual environment at first.

    . venv/bin/activate

Before running the webservice, you should init your database

    python manage.py tables

You could also apply fixtures

    python manage.py fixtures

Now you can safely run the webservice app

    python manage.py runserver

