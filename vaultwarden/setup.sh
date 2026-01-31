#!/bin/bash

# Ensure docker network exists
if ! docker network inspect nexus >/dev/null 2>&1; then
  docker network create nexus >/dev/null
fi

docker run -d --name vaultwarden \
    --network nexus \
    --env DOMAIN="https://vault.lamkin.dev" \
    --volume /mnt/vw-data/:/data/ \
    --restart unless-stopped \
    vaultwarden/server:latest
