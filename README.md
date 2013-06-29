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

    cp webservice/config.py.example webservice/config.py

and open `webservice/config.py` in your favourite text editor. Now fill the
DATABASE dictionary with your database configuration. Don't touch the `drivername`
value.

*Notice* In order to run the tests, you need to create a second database with
`_test` suffix.

##Configuring environment

First, you need to create and setup a new python environment.

    cd webservice
    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt

This will install all necessary python packages to your new virtual environment.

##Running

Remeber to enter your virtual environment at first.

    cd webservice
    . venv/bin/activate

Before running the webservice, you should init your database

    python manage.py tables

You could also apply fixtures

    python manage.py fixtures

Now you can safely run the webservice app

    python manage.py runserver

