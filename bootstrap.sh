#!/usr/bin/env bash

apt-get update
apt-get -y upgrade
apt-get install -y memcached python-virtualenv python-dev

# PostgreSQL
PG_VERSION=9.1
apt-get -y install "postgresql-$PG_VERSION" "postgresql-contrib-$PG_VERSION" "postgresql-server-dev-$PG_VERSION"
PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
PG_DIR="/var/lib/postgresql/$PG_VERSION/main"

# Edit postgresql.conf to change listen address to '*':
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"

# Append to pg_hba.conf to add password auth:
echo "host    all             all             all                     md5" >> "$PG_HBA"

# Restart so that all new config is loaded:
service postgresql restart

# Setting up CritiqueBrainz server
cd /vagrant/server
# TODO: Activate virtualenv
pip install -r requirements.txt
python manage.py create_db
python manage.py fixtures

# Setting up CritiqueBrainz client
cd /vagrant/client
# TODO: Activate virtualenv
pip install -r requirements.txt

# TODO: Start server and client automatically
