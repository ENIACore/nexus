#!/bin/bash

RAID_MOUNT=/mnt/RAID

# Create the network first (if it doesn't exist)
docker network create nexus

#--net=host enables DLNA (device discovery)
docker run -d \
    --name jellyfin \
    --network nexus \
    --volume ${RAID_MOUNT}/jelly/config:/config \
    --volume ${RAID_MOUNT}/jelly/cache:/cache \
    --mount type=bind,source=${RAID_MOUNT}/jelly/media,target=/media \
    --restart=unless-stopped \
    jellyfin/jellyfin:latest
