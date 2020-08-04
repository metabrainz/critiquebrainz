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
COMPOSE_PROJECT_NAME_ORIGINAL=critiquebrainz_test
# Project name is sanitized by Compose, so we need to do the same thing.
# See https://github.com/docker/compose/issues/2119.
COMPOSE_PROJECT_NAME=$(echo ${COMPOSE_PROJECT_NAME_ORIGINAL} | awk '{print tolower($0)}' | sed 's/[^a-z0-9]*//g')

if [[ ! -d "docker" ]]; then
    echo "This script must be run from the top level directory of the critiquebrainz-server source."
    exit -1
fi

function build_containers {
    docker-compose -f ${COMPOSE_FILE_LOC} \
                   -p ${COMPOSE_PROJECT_NAME} \
                build critiquebrainz_test
}

function bring_up_db {
    docker-compose -f ${COMPOSE_FILE_LOC} \
                   -p ${COMPOSE_PROJECT_NAME} \
                up -d db_test musicbrainz_db critiquebrainz_redis
}

function setup {
    echo "Running setup"
    # PostgreSQL Database initialization
    docker-compose -f ${COMPOSE_FILE_LOC} \
                   -p ${COMPOSE_PROJECT_NAME} \
                run --rm critiquebrainz_test dockerize \
                  -wait tcp://db_test:5432 -timeout 60s \
                bash -c "python3 manage.py init_db --skip-create-db --test-db"
}

function is_db_running {
    # Check if the database container is running
    containername="${COMPOSE_PROJECT_NAME}_db_test_1"
    res=`docker ps --filter "name=$containername" --filter "status=running" -q`
    if [[ -n "$res" ]]; then
        return 0
    else
        return 1
    fi
}

function is_db_exists {
    containername="${COMPOSE_PROJECT_NAME}_db_test_1"
    res=`docker ps --filter "name=$containername" --filter "status=exited" -q`
    if [[ -n "$res" ]]; then
        return 0
    else
        return 1
    fi
}

function dc_stop {
    # Stopping all unit test containers associated with this project
    docker-compose -f ${COMPOSE_FILE_LOC} \
                   -p ${COMPOSE_PROJECT_NAME} \
                stop
}

function dc_down {
    # Shutting down all unit test containers associated with this project
    docker-compose -f ${COMPOSE_FILE_LOC} \
                   -p ${COMPOSE_PROJECT_NAME} \
                down
}



if [[ "$1" == "-s" ]]; then
    echo "Stopping unit test containers"
    dc_stop
    exit 0
fi

if [[ "$1" == "-d" ]]; then
    echo "Running docker-compose down"
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
    echo "Running tests"
    docker-compose -f ${COMPOSE_FILE_LOC} \
                   -p ${COMPOSE_PROJECT_NAME} \
                run --rm critiquebrainz_test pytest "$@"
    dc_down
else
    # Else, we have containers, just run tests
    echo "Running tests"
    docker-compose -f ${COMPOSE_FILE_LOC} \
                   -p ${COMPOSE_PROJECT_NAME} \
                run --rm critiquebrainz_test pytest "$@"
fi
