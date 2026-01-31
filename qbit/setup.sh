#!/bin/bash
set -euo pipefail

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)

# Existing WireGuard config file
WIREGUARD_CONF="${BASE_DIR}/keys/wg0.conf"

# Host paths
QBIT_PATH="/mnt/RAID/qbit-data"
QBIT_CONFIG_PATH="${QBIT_PATH}/config"
QBIT_DATA_PATH="${QBIT_PATH}/data"

# Where hotio expects wg configs
WG_DIR="${QBIT_CONFIG_PATH}/wireguard"
WG_TARGET="${WG_DIR}/wg0.conf"

# Optional: set to enable LAN CIDR (i.e access WebUI directly from LAN; not only via nginx)
VPN_LAN_CIDR="192.168.1.0/24"

# --- sanity checks ---
if [[ ! -f "${WIREGUARD_CONF}" ]]; then
  echo "ERROR: WireGuard config not found at: ${WIREGUARD_CONF}" >&2
  exit 1
fi

mkdir -p "${WG_DIR}"

# Symlink into the config directory hotio mounts at /config
cp "${WIREGUARD_CONF}" "${WG_TARGET}"

# Ensure docker network exists
if ! docker network inspect nexus >/dev/null 2>&1; then
  docker network create nexus >/dev/null
fi

# Run hotio qBittorrent with built-in WireGuard VPN
docker run -d \
  --name qbittorrent \
  --network nexus \
  --restart unless-stopped \
  --cap-add=NET_ADMIN \
  -e PUID=1000 \
  -e PGID=1000 \
  -e UMASK=002 \
  -e TZ="America/Chicago" \
  -e VPN_ENABLED="true" \
  -e VPN_CONF="wg0" \
  -e VPN_PROVIDER="proton" \
  -e VPN_AUTO_PORT_FORWARD="true" \
  -e WEBUI_PORTS="8080/tcp" \
  -e VPN_LAN_LEAK_ENABLED="false" \
  -e VPN_HEALTHCHECK_ENABLED="false" \
  -e PRIVOXY_ENABLED="false" \
  -e UNBOUND_ENABLED="false" \
  -e VPN_LAN_NETWORK="${VPN_LAN_CIDR}" \
  -v "${QBIT_CONFIG_PATH}":/config \
  -v "${QBIT_DATA_PATH}":/data \
  ghcr.io/hotio/qbittorrent:latest

