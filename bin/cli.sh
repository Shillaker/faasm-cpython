#!/bin/bash

set -e

THIS_DIR=$(dirname $(readlink -f $0))
PROJ_ROOT=${THIS_DIR}/..

pushd ${PROJ_ROOT} > /dev/null

if [[ -z "${PYTHON_CLI_IMAGE}" ]]; then
    VERSION=$(cat VERSION)
    PYTHON_CLI_IMAGE=faasm/cpython:${VERSION}
fi

echo "Running ${PYTHON_CLI_IMAGE}"
INNER_SHELL=${SHELL:-"/bin/bash"}

docker-compose \
    up \
    --no-recreate \
    -d \
    cli 

docker-compose \
    exec \
    cli \
    ${INNER_SHELL}

popd > /dev/null
