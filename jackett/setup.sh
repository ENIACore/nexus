#!/bin/bash
source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_QBIT_PATH="${NEXUS_MEDIA_SERVICES_PATH}/qbit-data"
NEXUS_QBIT_CONFIG_PATH="${NEXUS_QBIT_PATH}"

NEXUS_JACKETT_OPT_DIR="${NEXUS_OPT_DIR}/jackett"
JACKETT_CONFIG_DIR="${NEXUS_MEDIA_SERVICES_PATH}/jackett/config"
JACKETT_DOWNLOADS_DIR="${NEXUS_QBIT_CONFIG_PATH}/jackett/downloads" # Places jackett blackholes in qbit mounted path, to allow for automatic watching

print_header "SETTING UP JACKETT INDEXER"

# Ensure media services path exists
require_dir "${NEXUS_MEDIA_SERVICES_PATH}" "Media services path"

# Create jackett directories
print_step "Creating Jackett directories"
mkdir -p "${JACKETT_CONFIG_DIR}"
mkdir -p "${JACKETT_DOWNLOADS_DIR}"

# Ensure docker network exists
if ! docker network inspect nexus-net >/dev/null 2>&1; then
    print_step "Creating Docker network 'nexus-net'"
    if ! docker network create \
        --driver bridge \
        --subnet 172.18.0.0/16 \
        --gateway 172.18.0.1 \
        nexus-net >/dev/null 2>&1; then
        print_error "Failed to create Docker network 'nexus-net' (subnet or gateway already in use, choose a new range)"
        exit 1
    fi
fi

# Run Jackett container
print_step "Starting Jackett container"
docker run -d \
    --name jackett \
    --network nexus-net \
    -e PUID=1000 \
    -e PGID=1000 \
    -e TZ=Etc/UTC \
    -e AUTO_UPDATE=true \
    --volume "${JACKETT_CONFIG_DIR}:/config" \
    --volume "${JACKETT_DOWNLOADS_DIR}:/downloads" \
    --restart=unless-stopped \
    lscr.io/linuxserver/jackett:latest

# -p 9117:9117 \

if [ $? -eq 0 ]; then
    print_success "Jackett container started successfully"
    print_info ""
    print_info "Next steps:"
    print_info "1. Access Jackett at jackett.${NEXUS_DOMAIN} if configured"
    print_info "2. Configure indexers via the Jackett web UI"
    print_info "3. Copy the API key from the web UI for use with downstream apps (Sonarr, Radarr, etc.)"
else
    print_error "Failed to start Jackett container"
    exit 1
fi
