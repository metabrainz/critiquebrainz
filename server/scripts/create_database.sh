#!/bin/bash
# Usage:
#   ./create-database.sh database-name database-user

# fetch args
if [ $# -ne 2 ]; then
    echo "Usage:"
    echo
    echo "  $0 database-name database-user"
    echo
    exit 1
fi

dbname=$1
dbuser=$2

# check if database already exists
sudo -u postgres psql -d $dbname -c "" &> /dev/null

if [ $? -ne 0 ]; then
    sudo -u postgres createdb -O $dbuser $dbname &> /dev/null
    exit $?
fi

exit 0
