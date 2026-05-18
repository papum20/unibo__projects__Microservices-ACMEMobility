#!/bin/bash

set -a 
source src/bash-scripts/scripts.env
./src/bash-scripts/env-cleanup.sh

set -a
source src/bash-scripts/clean.env.generated

export DOLLAR='$'
envsubst < $DOCKER_COMPOSE_TEMPLATE > $DOCKER_COMPOSE_FILE

echo "Successfully compiled '$DOCKER_COMPOSE_TEMPLATE' to '$DOCKER_COMPOSE_FILE'"
