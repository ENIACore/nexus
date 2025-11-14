#!/bin/bash

# Create the network first (if it doesn't exist)
docker network create nexus

docker run -d --name vaultwarden \
    --network nexus \
    --env DOMAIN="https://vault.lamkin.dev" \
    --volume /mnt/vw-data/:/data/ \
    --restart unless-stopped \
    vaultwarden/server:latest
