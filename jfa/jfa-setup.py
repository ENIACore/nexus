#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_JFA_OPT_DIR="${NEXUS_OPT_DIR}/jfa"
JFA_CONFIG_DIR="${NEXUS_MEDIA_SERVICES_PATH}/jfa/config"
JELLY_CONFIG_DIR="${NEXUS_MEDIA_SERVICES_PATH}/jelly/config"

echo "Jelly config dir is: ${JELLY_CONFIG_DIR}"

print_header "SETTING UP JFA-GO (JELLYFIN ACCOUNT MANAGER)"

# Ensure base path exists
require_dir "${NEXUS_MEDIA_SERVICES_PATH}" "Media services path"

# Create JFA directories
print_step "Creating JFA directories"
mkdir -p "${JFA_CONFIG_DIR}"

# Ensure docker network exists (reuse same as Jellyfin)
if ! docker network inspect nexus-net >/dev/null 2>&1; then
    print_step "Creating Docker network 'nexus-net'"

    if ! docker network create \
        --driver bridge \
        --subnet 172.18.0.0/16 \
        --gateway 172.18.0.1 \
        nexus-net >/dev/null 2>&1; then
        print_error "Failed to create Docker network 'nexus-net'"
        exit 1
    fi
fi

# Run JFA-Go container
print_step "Starting JFA-Go container"
docker run -d \
    --name jfa-go \
    --network nexus-net \
    --volume "${JFA_CONFIG_DIR}:/data" \
    --volume "${JELLY_CONFIG_DIR}:/jf" \
    --volume /etc/localtime:/etc/localtime:ro \
    --restart=unless-stopped \
    hrfee/jfa-go

#    -p 8056:8056 \

if [ $? -eq 0 ]; then
    print_success "JFA-Go container started successfully"
    print_info ""
    print_info "Next steps:"
    print_info "1. Access JFA-Go at http://localhost:8056"
    print_info "2. Connect it to your Jellyfin instance (http://jellyfin:8096 on the Docker network)"
    print_info "3. Configure invite links and user settings"
else
    print_error "Failed to start JFA-Go container"
    exit 1
fi
