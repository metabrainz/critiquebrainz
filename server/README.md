critiquebrainz-server
=====================

A GSoC project for MetaBrainz Foundation. 

##Requirements

* PostgreSQL (tested on 9.1.9)
* Python (tested on 2.7.4)
* virtualenv

##How to start

###Creating virtualenv (optional)

This step is not required, but highly recommended for development instances.
You may find it useful to keep libraries needed by CritiqueBrainz seperated
from your global python libraries. To achieve this, you will need a
`virtualenv` package. You may install it with `pip` or `apt-get` on Debian/Ubuntu
systems

    sudo pip install virtualenv (or)
    sudo apt-get install python-virtualenv

Then, `cd` into your `critiquebrainz/` directory and run

    scripts/virtualenv.sh

It will create a symbolic link `env` to virtualenv's entry point in your
`critiquebrainz/` directory. To enter newly created virtualenv, type in

    source ./env

You should do this before executing any other file from CritiqueBrainz package. 

###Installing dependencies

If you're in your desired python environment, simply run

    pip install -r requirements.txt

to install all required dependencies.

###Preparing database

First, you need to configure your critiquebrainz instance. Copy the skeleton
configuration

    cp critiquebrainz/config.py.example critiquebrainz/config.py

Then, open `critiquebrainz/config.py` in your favourite text editor and fill in
the fields in angle brackets in `SQLALCHEMY_DATABASE_URI` body.

Now, you may want to create and configure the database with

    python manage.py create_db

This command will
* create new PostgreSQL role, if needed
* create new PostgreSQL database, if needed
* register `uuid-ossp` PostgreSQL extension, if needed

You may also want to update the newly created database with default schema
and testing data. To do this type

    python manage.py fixtures

###Preparing login 

Before you begin using authentication with Twitter and/or MusicBrainz accounts, 
you need to set `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`, 
`MUSICBRAINZ_CLIENT_ID`, and `MUSICBRAINZ_CLIENT_SECRET` in 
`critiquebrainz/config.py`. To obtain these keys, you need to register your
client app on Twitter and Musicbrainz websites.

**Note** `<your domain>` field in the urls listed below should probably be set
to `127.0.0.1:5000`, if you plan to run your CritiqueBrainz instance locally 
in development mode.

####Twitter
You need Twitter account to register your application. Then head to
https://dev.twitter.com/apps/new and follow the instructions. In `Callback URL`
field type

    http://<your domain>/login/twitter/post

Finally, save the obtained `Consumer key` and `Consumer secret` fields in your
`config.py` fields `TWITTER_CONSUMER_KEY` and `TWITTER_CONSUMER_SECRET` 
respectively.

####MusicBrainz
You need MusicBrainz account to register your application. Then head to
http://musicbrainz.org/account/applications/register and follow the instructions.
In `Callback URL` field type

    http://<your domain>/login/musicbrainz/post

Finally, save the obtained `OAuth Client ID` and `OAuth Client Secret` fields 
in your `config.py` fields `MUSICBRAINZ_CLIENT_ID` and `MUSICBRAINZ_CLIENT_SECRET` 
respectively.

##Running

Remeber to enter your virtual environment first.

    source ./env

Now you can safely run the webservice app

    python manage.py runserver

