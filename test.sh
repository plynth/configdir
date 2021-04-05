#!/bin/bash

set -Eeuo pipefail

[ -n "${DEBUG:-}" ] && set -x

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

docker build -t configdir:test .

docker run \
    -it --rm \
    -v "$DIR/tests:$DIR/tests" \
    -w "$DIR/tests" \
    configdir:test \
    pytest "$@"