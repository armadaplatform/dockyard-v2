#!/bin/bash

# This file is an executable script for docker-registry-cleanup.sh.
# We have to set some parameters before executing docker-registry-cleanup.sh.
# The docker-registry-cleanup.sh exit status determines if launching garbage collector 
# is required.

function cleanup() {
    CMD="/opt/dockyard-v2/scripts/docker-registry-cleanup.sh"
    REGISTRY_URL="localhost:80" REGISTRY_DIR="/repository" bash $CMD > /dev/null
    return $? 
}

function gc() {
    CFG="/etc/docker/registry/config.yml"
    /go/bin/registry garbage-collect $CFG > /dev/null
}

cleanup && gc
