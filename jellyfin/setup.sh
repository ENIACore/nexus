#!/bin/bash

# Create necessary directories
mkdir -p /mnt/storage/jelly/config
mkdir -p /mnt/storage/jelly/cache
mkdir -p /mnt/storage/jelly/media

# Create the network first (if it doesn't exist)
docker network create nexus

#--net=host enables DLNA (device discovery)
docker run -d \
    --name jellyfin \
    --network nexus \
    --volume /mnt/storage/jelly/config:/config \
    --volume /mnt/storage/jelly/cache:/cache \
    --mount type=bind,source=/mnt/storage/jelly/media,target=/media \
    --restart=unless-stopped \
    jellyfin/jellyfin:latest
