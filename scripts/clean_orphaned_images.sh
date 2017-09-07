#!/bin/bash

set -e 

REGISTRY_URL="localhost" \
REGISTRY_DIR="/repository" \
bash /opt/dockyard-v2/scripts/docker-registry-cleanup.sh 

/go/bin/registry garbage-collect "/etc/docker/registry/config.yml"
