#!/bin/bash
#
# Build image from the currently checked out version of CritiqueBrainz
# and push it to the Docker Hub, with an optional tag (by default "beta").
#
# Usage:
#   $ ./push.sh [tag]

cd "$(dirname "${BASH_SOURCE[0]}")/../"

TAG=${1:-beta}
docker build -t metabrainz/critiquebrainz:$TAG \
        --build-arg GIT_COMMIT_SHA=$(git rev-parse HEAD) .
docker push metabrainz/critiquebrainz:$TAG
