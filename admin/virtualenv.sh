#!/bin/bash
# Usage:
#   ./virtualenv.sh virtual-env-directory

# fetch args

if [ $# -ge 2 ]; then
    echo "Usage:"
    echo
    echo "  $0 [virtual-env-directory=venv]"
    echo
    exit 1
fi

venvdir=$1
: ${venvdir:="venv"}

virtualenv $venvdir

if [ $? -ne 0 ]; then
    echo "Failed to create virtual end."
    echo
    exit 1
else
    echo "Created virtualenv in: $venvdir"
    echo
fi

ln -s $venvdir/bin/activate env

echo "Created symbolic link to $venvdir/bin/activate in: env"
echo "To enter newly created virtualenv type:"
echo
echo "  source ./env"
echo
