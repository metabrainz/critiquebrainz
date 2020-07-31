#!/bin/bash

POSTGRES_CB_URI="postgresql://critiquebrainz:critiquebrainz@db/critiquebrainz"

if [[ ! -d "docker" ]]; then
    echo "This script must be run from the top level directory of the critiquebrainz source."
    exit -1
fi

function invoke_docker_compose {
    exec docker-compose -f docker/docker-compose.dev.yml \
                -p critiquebrainz \
                "$@"
}

function invoke_docker_compose_test {
    exec docker-compose -f docker/docker-compose.test.yml \
                -p critiquebrainz_test \
                "$@"
}

function invoke_manage {
    invoke_docker_compose run --rm critiquebrainz \
            python3 manage.py \
            "$@"
}

function open_psql_shell {
    invoke_docker_compose run --rm critiquebrainz psql \
        ${POSTGRES_CB_URI}
}

# Arguments following "manage" are passed to manage.py inside a new web container.
if [[ "$1" == "manage" ]]; then shift
    echo "Running manage.py..."
    invoke_manage "$@"
elif [[ "$1" == "bash" ]]; then
    echo "Running bash..."
    invoke_docker_compose run --rm critiquebrainz bash
elif [[ "$1" == "shell" ]]; then
    echo "Running flask shell..."
    invoke_docker_compose run --rm critiquebrainz flask shell
elif [[ "$1" == "psql" ]]; then
    echo "Connecting to postgresql..."
    open_psql_shell
elif [[ "$1" == "test" ]]; then shift
    echo "Running docker-compose test..."
    invoke_docker_compose_test "$@"
else
    echo "Running docker-compose with the given command..."
    invoke_docker_compose "$@"
fi
