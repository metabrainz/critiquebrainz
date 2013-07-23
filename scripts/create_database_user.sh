#!/bin/bash
# Usage:
#   ./create-database-user.sh database-user database-password

# fetch args
if [ $# -ne 2 ]; then
    echo "Usage:"
    echo
    echo "  $0 database-user database-password"
    echo
    exit 1
fi

dbuser=$1
dbpass=$2

# check if user already exists
cnt=$(sudo -u postgres psql -t -A -c "SELECT COUNT(*) FROM pg_user WHERE usename = '$1';")

if [ $cnt -eq 0 ]; then
    sudo -u postgres psql -c "CREATE ROLE $1 PASSWORD '$2' NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN;" &> /dev/null
    exit $?
fi

exit 0
