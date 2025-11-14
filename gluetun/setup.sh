#!/bin/bash

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)
GLUETUN_SECRETS="${BASE_DIR}/keys/gluetun.sh"
source "${GLUETUN_SECRETS}"

# Port mappings
# QBT_TORRENTING_PORT=6881
# QBT_WEBUI_PORT=8080 - Removed, reverse proxy accessible via nexus network

docker run -d --name gluetun --cap-add=NET_ADMIN --device /dev/net/tun \
  --network nexus \
  -p 6881 \
  -e VPN_SERVICE_PROVIDER=protonvpn \
  -e VPN_TYPE=wireguard \
  -e WIREGUARD_PRIVATE_KEY="${WIREGUARD_PRIVATE_KEY}" \
  -e SERVER_COUNTRIES="United States" \
  -e SERVER_CITIES="San Jose" \
  qmcgaw/gluetun
