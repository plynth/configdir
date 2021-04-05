#!/bin/bash

set -Eeuo pipefail

[ -n "${DEBUG:-}" ] && set -x

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
	
docker build -t configdir:poetry --target poetry .
docker run -it --rm \
    -v "$PWD:$PWD" \
    -w "$PWD" \
    --entrypoint /bin/bash \
    "configdir:poetry"