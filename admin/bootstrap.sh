#!/bin/sh -e

apt-get update
apt-get install -y build-essential python3-pip python3-dev memcached curl git \
    libffi-dev libssl-dev libxml2-dev libxslt1-dev libffi-dev libssl-dev

# PostgreSQL
PG_VERSION=9.3
apt-get -y install "postgresql-$PG_VERSION" "postgresql-contrib-$PG_VERSION" "postgresql-server-dev-$PG_VERSION"
PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
PG_DIR="/var/lib/postgresql/$PG_VERSION/main"

# Setting up PostgreSQL access
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"
echo "host all all all trust" >> "$PG_HBA"
service postgresql restart

# Setting up server
cd /vagrant
pip3 install -r requirements.txt
python3 manage.py init_db

# Node
curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -
apt-get install -y nodejs

python3 manage.py build_static

# Installing requirements for documentation
cd /vagrant/docs
pip3 install -r requirements.txt
