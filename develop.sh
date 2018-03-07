#!/bin/bash

if [[ ! -d "docker" ]]; then
    echo "This script must be run from the top level directory of the critiquebrainz-server source."
    exit -1
fi

# invoke docker, but ungrep noisy influx log messages that I can't turn off
docker-compose -f docker/docker-compose.dev.yml build && docker-compose -f docker/docker-compose.dev.yml up