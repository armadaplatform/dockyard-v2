#!/usr/bin/env bash

status_code=$(curl -s -o /dev/null -w "%{http_code}" localhost/v2/_catalog)
if [[ status_code -ne 200 ]]; then
    echo "Registry did not respond with HTTP 200"
    exit 1
fi
exit 0
