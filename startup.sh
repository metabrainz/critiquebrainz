#!/usr/bin/env bash

# Starting servers
apt-get install -y screen
screen -S server -d -m python /vagrant/server/manage.py runserver -t 0.0.0.0 -p 5000
screen -S client -d -m python /vagrant/client/manage.py runserver -t 0.0.0.0 -p 5001
