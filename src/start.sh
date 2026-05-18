#!/bin/bash

set -a
source src/bash-scripts/scripts.env

./src/bash-scripts/compile-dockercompose.sh

docker compose -f $DOCKER_COMPOSE_FILE --env-file $CLEAN_ENV up --build