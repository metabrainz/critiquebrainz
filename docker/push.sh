#!/bin/bash
#
# Build image from the currently checked out version of CritiqueBrainz
# and push it to the Docker Hub, with an optional tag (by default "beta").
#
# Usage:
#   $ ./push.sh [env] [tag]

cd "$(dirname "${BASH_SOURCE[0]}")/../"

ENV=${1:-beta}
TAG=${2:-beta}
docker build -t metabrainz/critiquebrainz:$TAG \
        --build-arg GIT_COMMIT_SHA=$(git rev-parse HEAD) \
        --build-arg DEPLOY_ENV=$ENV .
docker push metabrainz/critiquebrainz:$TAG
