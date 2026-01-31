#!/bin/bash

RAID_MOUNT=/mnt/RAID

# Ensure docker network exists
if ! docker network inspect nexus >/dev/null 2>&1; then
  docker network create nexus >/dev/null
fi

#--net=host enables DLNA (device discovery)
docker run -d \
    --name jellyfin \
    --network nexus \
    --volume ${RAID_MOUNT}/jelly/config:/config \
    --volume ${RAID_MOUNT}/jelly/cache:/cache \
    --mount type=bind,source=${RAID_MOUNT}/jelly/media,target=/media \
    --restart=unless-stopped \
    jellyfin/jellyfin:latest
