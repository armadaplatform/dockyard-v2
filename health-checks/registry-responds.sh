#!/usr/bin/env bash

output=$(curl -s -w "\n%{http_code}" localhost:5001/debug/health)
status_code=$(echo "$output" | tail -n 1)
if [[ status_code -ne 200 ]]; then
    response=$(echo "$output" | head -n -1)
    echo "Response from dockyard: HTTP $status_code: $response"
    exit 1
fi
exit 0
