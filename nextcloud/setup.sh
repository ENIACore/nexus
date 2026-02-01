#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_NEXTCLOUD_OPT_DIR="${NEXUS_OPT_DIR}/nextcloud"
NEXUS_NEXTCLOUD_DATA_DIR="/mnt/nextcloud-data"

print_header "SETTING UP NEXTCLOUD ALL-IN-ONE"

# Create nextcloud data directory
print_step "Creating Nextcloud data directory at ${NEXUS_NEXTCLOUD_DATA_DIR}"
mkdir -p "${NEXUS_NEXTCLOUD_DATA_DIR}"

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

# Run Nextcloud AIO master container
print_step "Starting Nextcloud AIO master container"
print_info "Using beta version due to breaking release"
print_info "See https://github.com/nextcloud/all-in-one#how-to-switch-the-channel to switch back to latest"

docker run -d \
    --init \
    --sig-proxy=false \
    --network nexus-net \
    --name nextcloud-aio-mastercontainer \
    --restart always \
    --env APACHE_PORT=11000 \
    --env APACHE_IP_BINDING=0.0.0.0 \
    --env APACHE_ADDITIONAL_NETWORK="nexus" \
    --env SKIP_DOMAIN_VALIDATION=true \
    --env NEXTCLOUD_DATADIR="${NEXUS_NEXTCLOUD_DATA_DIR}" \
    --volume nextcloud_aio_mastercontainer:/mnt/docker-aio-config \
    --volume /var/run/docker.sock:/var/run/docker.sock:ro \
    ghcr.io/nextcloud-releases/all-in-one:beta

if [ $? -eq 0 ]; then
    print_success "Nextcloud AIO master container started successfully"
    print_info ""
    print_info "Next steps:"
    print_info "1. Access Nextcloud AIO at https://<server-ip>:11000 (NOT the subdomain) (nginx must proxy to AIO container)"
    print_info "2. Complete the initial setup through the web interface"
    print_info "3. Data will be stored in ${NEXUS_NEXTCLOUD_DATA_DIR}"
else
    print_error "Failed to start Nextcloud AIO master container"
    exit 1
fi
