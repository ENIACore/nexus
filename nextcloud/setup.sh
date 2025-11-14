#!/bin/bash

# Create the network first (if it doesn't exist)
docker network create nexus

docker run -d \
    --init \
    --sig-proxy=false \
    --network nexus \
    --name nextcloud-aio-mastercontainer \
    --restart always \
    --env APACHE_PORT=11000 \
    --env APACHE_IP_BINDING=0.0.0.0 \
    --env APACHE_ADDITIONAL_NETWORK="nexus" \
    --env SKIP_DOMAIN_VALIDATION=true \
    --env NEXTCLOUD_DATADIR="/mnt/nextcloud-data" \
    --volume nextcloud_aio_mastercontainer:/mnt/docker-aio-config \
    --volume /var/run/docker.sock:/var/run/docker.sock:ro \
    ghcr.io/nextcloud-releases/all-in-one:latest
