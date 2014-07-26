#!/usr/bin/env bash

# Starting servers
apt-get install -y screen
screen -S server -d -m python /vagrant/run.py
