#!/usr/bin/env bash

apt-get update
apt-get install -y memcached python-virtualenv python-dev screen make

# PostgreSQL
PG_VERSION=9.1
apt-get -y install "postgresql-$PG_VERSION" "postgresql-contrib-$PG_VERSION" "postgresql-server-dev-$PG_VERSION"
PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
PG_DIR="/var/lib/postgresql/$PG_VERSION/main"

# Setting up PostgreSQL access
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"
echo "host all all all trust" >> "$PG_HBA"
service postgresql restart

# Setting up CritiqueBrainz server
cd /vagrant
# TODO: Activate virtualenv
pip install -r requirements.txt
python manage.py create_db
python manage.py fixtures
