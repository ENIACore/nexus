#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_VAULT_OPT_DIR="${NEXUS_OPT_DIR}/vault"
NEXUS_VAULT_DATA_DIR="/mnt/vw-data"

print_header "SETTING UP VAULTWARDEN PASSWORD MANAGER"

# Create vaultwarden data directory
print_step "Creating Vaultwarden data directory at ${NEXUS_VAULT_DATA_DIR}"
mkdir -p "${NEXUS_VAULT_DATA_DIR}"

# Ensure docker network exists
if ! docker network inspect nexus >/dev/null 2>&1; then
    print_step "Creating Docker network 'nexus'"
    docker network create nexus >/dev/null
fi

# Run Vaultwarden container
print_step "Starting Vaultwarden container"
docker run -d \
    --name vaultwarden \
    --network nexus \
    --env DOMAIN="https://${NEXUS_VAULT_SUBDOMAIN}" \
    --volume "${NEXUS_VAULT_DATA_DIR}:/data/" \
    --restart unless-stopped \
    vaultwarden/server:latest

if [ $? -eq 0 ]; then
    print_success "Vaultwarden container started successfully"
    print_info ""
    print_info "Next steps:"
    print_info "1. Create admin account through the web interface"
    print_info "2. Data will be stored in ${NEXUS_VAULT_DATA_DIR}"
else
    print_error "Failed to start Vaultwarden container"
    exit 1
fi
