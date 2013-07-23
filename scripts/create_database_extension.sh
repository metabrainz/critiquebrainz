#!/bin/bash
# Usage:
#   ./create-database-extension.sh database-name extension-name

# fetch args
if [ $# -ne 2 ]; then
    echo "Usage:"
    echo
    echo "  $0 database-name extension-name"
    echo
    exit 1
fi

dbname=$1
extname=$2

sudo -u postgres psql -t -A -c "CREATE EXTENSION IF NOT EXISTS \"$extname\";" $dbname &> /dev/null 

exit $?
