#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_JELLY_OPT_DIR="${NEXUS_OPT_DIR}/jelly"
JELLY_CONFIG_DIR="${NEXUS_RAID_MOUNT}/jelly/config"
JELLY_CACHE_DIR="${NEXUS_RAID_MOUNT}/jelly/cache"
JELLY_MEDIA_DIR="${NEXUS_RAID_MOUNT}/jelly/media"

print_header "SETTING UP JELLYFIN MEDIA SERVER"

# Ensure RAID mount exists
require_dir "${NEXUS_RAID_MOUNT}" "RAID mount point"

# Create jellyfin directories
print_step "Creating Jellyfin directories"
mkdir -p "${JELLY_CONFIG_DIR}"
mkdir -p "${JELLY_CACHE_DIR}"
mkdir -p "${JELLY_MEDIA_DIR}"

# Ensure docker network exists
if ! docker network inspect nexus >/dev/null 2>&1; then
    print_step "Creating Docker network 'nexus'"
    docker network create --driver bridge --subnet 172.18.0.0/16 nexus >/dev/null
fi

# Run Jellyfin container
print_step "Starting Jellyfin container"
docker run -d \
    --name jellyfin \
    --network nexus \
    --volume "${JELLY_CONFIG_DIR}:/config" \
    --volume "${JELLY_CACHE_DIR}:/cache" \
    --mount type=bind,source="${JELLY_MEDIA_DIR}",target=/media \
    --restart=unless-stopped \
    jellyfin/jellyfin:latest

if [ $? -eq 0 ]; then
    print_success "Jellyfin container started successfully"
    print_info ""
    print_info "Next steps:"
    print_info "1. Access Jellyfin at ${NEXUS_JELLY_SUBDOMAIN} if configured"
    print_info "2. Add media files to ${JELLY_MEDIA_DIR}"
    print_info "Note: --net=host can be used to enable DLNA (device discovery) if needed"
else
    print_error "Failed to start Jellyfin container"
    exit 1
fi
