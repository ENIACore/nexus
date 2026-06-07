#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_QBIT_OPT_DIR="${NEXUS_OPT_DIR}/qbit"
NEXUS_QBIT_PATH="${NEXUS_MEDIA_SERVICES_PATH}/qbit-data"
NEXUS_QBIT_CONFIG_PATH="${NEXUS_QBIT_PATH}"
#NEXUS_QBIT_DATA_PATH="${NEXUS_QBIT_PATH}/data"
NEXUS_QBIT_WG_DIR="${NEXUS_QBIT_PATH}/wireguard"
NEXUS_QBIT_WG_TARGET="${NEXUS_QBIT_WG_DIR}/wg0.conf"

# WireGuard config file
NEXUS_WG_CONF="${NEXUS_ETC_DIR}/keys/wg0.conf"

# Docker network configuration
NEXUS_DOCKER_NETWORK="nexus-net"
NEXUS_DOCKER_SUBNET="172.18.0.0/16"
NEXUS_DOCKER_GATEWAY="172.18.0.1"

# LAN CIDR (access WebUI directly from LAN; not only via nginx)
# NOTE: Do NOT add the Docker subnet here — it's the container's own
# directly-attached network and including it causes a route conflict
# in hotio's startup (eth0 is already on 172.18.0.0/16). Container-to-
# container traffic on nexus-net bypasses the VPN automatically.
VPN_LAN_CIDR="192.168.1.0/24"

print_header "SETTING UP QBITTORRENT WITH WIREGUARD VPN"

# Ensure WireGuard config exists
require_file "${NEXUS_WG_CONF}" "WireGuard config file (wg0.conf)"

# Ensure media services path exists
require_dir "${NEXUS_MEDIA_SERVICES_PATH}" "Media services path"

# Create qBittorrent directories
print_step "Creating qBittorrent directories"
mkdir -p "${NEXUS_QBIT_WG_DIR}"
#mkdir -p "${NEXUS_QBIT_DATA_PATH}"

# Copy WireGuard config
print_step "Copying WireGuard config to qBittorrent config directory"
cp "${NEXUS_WG_CONF}" "${NEXUS_QBIT_WG_TARGET}"

# Ensure docker network exists
if ! docker network inspect "${NEXUS_DOCKER_NETWORK}" >/dev/null 2>&1; then
    print_step "Creating Docker network '${NEXUS_DOCKER_NETWORK}'"

    if ! docker network create \
        --driver bridge \
        --subnet "${NEXUS_DOCKER_SUBNET}" \
        --gateway "${NEXUS_DOCKER_GATEWAY}" \
        "${NEXUS_DOCKER_NETWORK}" >/dev/null 2>&1; then
        print_error "Failed to create Docker network '${NEXUS_DOCKER_NETWORK}' (subnet or gateway already in use, choose a new range)"
        exit 1
    fi
fi

# Run hotio qBittorrent with built-in WireGuard VPN
print_step "Starting qBittorrent container with WireGuard VPN"
docker run -d \
    --name qbittorrent \
    --network "${NEXUS_DOCKER_NETWORK}" \
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
    -v "${NEXUS_QBIT_CONFIG_PATH}":/config \
    ghcr.io/hotio/qbittorrent:latest

#-v "${NEXUS_QBIT_DATA_PATH}":/data \

if [ $? -eq 0 ]; then
    print_success "qBittorrent container started successfully"
    print_info ""
    print_info "Next steps:"
    print_info "1. Access qBittorrent WebUI at ${NEXUS_QBIT_SUBDOMAIN} if configured"
    print_info "2. Validate VPN connection via docker logs"
    #print_info "3. Downloads will be stored in ${NEXUS_QBIT_DATA_PATH}"
else
    print_error "Failed to start qBittorrent container"
    exit 1
fi
