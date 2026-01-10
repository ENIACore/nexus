#!/bin/bash

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)
GLUETUN_SECRETS="${BASE_DIR}/keys/gluetun.sh"
source "${GLUETUN_SECRETS}"

# Port mappings
# QBT_TORRENTING_PORT=6881
# QBT_WEBUI_PORT=8080 - Removed, reverse proxy accessible via nexus network

CITY="Miami" # South Florida
#CITY="Atlanta" # North Florida
#CITY="San Jose" # North California

PORT_FWD_UP='/bin/sh -c "wget -O- --retry-connrefused --post-data \"json={\\\"listen_port\\\":{{PORT}},\\\"random_port\\\":false,\\\"upnp\\\":false}\" http://127.0.0.1:8080/api/v2/app/setPreferences 2>&1"'

PORT_FWD_DOWN='/bin/sh -c "wget -O- --retry-connrefused --post-data \"json={\\\"listen_port\\\":0}\" http://127.0.0.1:8080/api/v2/app/setPreferences 2>&1"'

docker run -d --name gluetun --cap-add=NET_ADMIN --device /dev/net/tun \
  --network nexus \
  -p 6881 \
  -e VPN_SERVICE_PROVIDER=protonvpn \
  -e OPENVPN_USER="${OPENVPN_USER}" \
  -e OPENVPN_PASSWORD="${OPENVPN_PASSWORD}" \
  -e SERVER_COUNTRIES="United States" \
  -e SERVER_CITIES=${CITY} \
  -e PORT_FORWARD_ONLY=on \
  -e VPN_PORT_FORWARDING=on \
  -e "VPN_PORT_FORWARDING_UP_COMMAND=${PORT_FWD_UP}" \
  -e "VPN_PORT_FORWARDING_DOWN_COMMAND=${PORT_FWD_DOWN}" \
  qmcgaw/gluetun
