#!/bin/bash


set -a
source src/bash-scripts/scripts.env

docker compose -f $DOCKER_COMPOSE_FILE down