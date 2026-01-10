#!/bin/bash

export \
  RAID_MOUNT=/mnt/RAID
  QBT_LEGAL_NOTICE=confirm \
  QBT_VERSION=latest \
  QBT_TORRENTING_PORT=6881 \
  QBT_WEBUI_PORT=8080 \
  QBT_CONFIG_PATH="${RAID_MOUNT}/qbit-data/config" \
  QBT_DOWNLOADS_PATH="${RAID_MOUNT}/qbit-data/downloads"
docker run \
  -d \
  --network=container:gluetun \
  --name qbittorrent-nox \
  --read-only \
  --rm \
  --stop-timeout 1800 \
  --tmpfs /tmp \
  -e QBT_LEGAL_NOTICE \
  -e QBT_TORRENTING_PORT \
  -e QBT_WEBUI_PORT \
  -v "$QBT_CONFIG_PATH":/config \
  -v "$QBT_DOWNLOADS_PATH":/downloads \
  qbittorrentofficial/qbittorrent-nox:${QBT_VERSION}

# Ports disabled due to port forwarding by gluetun
#-p "$QBT_TORRENTING_PORT":"$QBT_TORRENTING_PORT"/tcp \
#-p "$QBT_TORRENTING_PORT":"$QBT_TORRENTING_PORT"/udp \

# Ports disabled due to port forwarding by nginx
#-p "$QBT_WEBUI_PORT":"$QBT_WEBUI_PORT"/tcp \
