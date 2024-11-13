#!/bin/bash

# UNIT TESTS
# ./test.sh                build unit test containers, bring up, make database, test, bring down
# for development:
# ./test.sh -u             build unit test containers, bring up background and load database if needed
# ./test.sh -b             build unit test containers
# ./test.sh [params]       run unit tests, passing optional params to inner test
# ./test.sh -s             stop unit test containers without removing
# ./test.sh -d             stop unit test containers and remove them

COMPOSE_FILE_LOC=docker/docker-compose.test.yml
COMPOSE_PROJECT_NAME=critiquebrainz_test

if [[ ! -d "docker" ]]; then
    echo "This script must be run from the top level directory of the critiquebrainz-server source."
    exit -1
fi

echo "Checking docker compose version"
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

function invoke_docker_compose_cmd {
    $DOCKER_COMPOSE_CMD \
      -f ${COMPOSE_FILE_LOC} \
      -p ${COMPOSE_PROJECT_NAME} \
      "$@"
}

function build_containers {
    invoke_docker_compose_cmd build critiquebrainz
}

function bring_up_db {
    invoke_docker_compose_cmd up -d db musicbrainz_db critiquebrainz_redis
}

function setup {
    echo "Running setup"
    # PostgreSQL Database initialization
    invoke_docker_compose_cmd \
      run --rm critiquebrainz dockerize \
      -wait tcp://db:5432 -timeout 60s \
      bash -c "python3 manage.py init_db"
    
    invoke_docker_compose_cmd \
      run --rm critiquebrainz bash scripts/download-import-bookbrainz-dump.sh

    invoke_docker_compose_cmd \
      run --rm critiquebrainz bash scripts/add-test-bookbrainz-data.sh
                   
}

function is_db_running {
    # Check if the database container is running
    containername="${COMPOSE_PROJECT_NAME}-db-1"
    res=`docker ps --filter "name=$containername" --filter "status=running" -q`
    if [[ -n "$res" ]]; then
        return 0
    else
        return 1
    fi
}

function is_db_exists {
    containername="${COMPOSE_PROJECT_NAME}-db-1"
    res=`docker ps --filter "name=$containername" --filter "status=exited" -q`
    if [[ -n "$res" ]]; then
        return 0
    else
        return 1
    fi
}

function dc_stop {
    # Stopping all unit test containers associated with this project
    invoke_docker_compose_cmd stop
}

function dc_down {
    # Shutting down all unit test containers associated with this project
    invoke_docker_compose_cmd down
}

function run_tests {
    echo "Running tests"
    invoke_docker_compose_cmd \
      run --rm critiquebrainz \
      dockerize -wait tcp://db:5432 -timeout 60s \
      dockerize -wait tcp://musicbrainz_db:5432 -timeout 600s \
      pytest --junitxml=reports/tests.xml "$@"
}



if [[ "$1" == "-s" ]]; then
    echo "Stopping unit test containers"
    dc_stop
    exit 0
fi

if [[ "$1" == "-d" ]]; then
    echo "Running $DOCKER_COMPOSE_CMD down"
    dc_down
    exit 0
fi

# if -u flag, bring up db, run setup, quit
if [[ "$1" == "-u" ]]; then
    is_db_exists
    DB_EXISTS=$?
    is_db_running
    DB_RUNNING=$?
    if [[ ${DB_EXISTS} -eq 0 || ${DB_RUNNING} -eq 0 ]]; then
        echo "Database is already up, doing nothing"
    else
        echo "Building containers"
        build_containers
        echo "Bringing up DB"
        bring_up_db
        setup
    fi
    exit 0
fi

is_db_exists
DB_EXISTS=$?
is_db_running
DB_RUNNING=$?
if [[ ${DB_EXISTS} -eq 1 && ${DB_RUNNING} -eq 1 ]]; then
    # If no containers, build them, run setup then run tests, then bring down
    build_containers
    bring_up_db
    setup
    run_tests "$@"
    RET=$?
    dc_down
    exit $RET
else
    # Else, we have containers, just run tests
    run_tests "$@"
fi
