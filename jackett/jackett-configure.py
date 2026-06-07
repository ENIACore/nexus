#!/bin/bash
# Used to add Jackett credentials to /config/data/nova3/engines/jackett.json in qbittorrent
source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_JACKETT_OPT_DIR="${NEXUS_OPT_DIR}/jackett"
QBIT_CONTAINER_NAME="qbittorrent"
JACKETT_CONFIG_PATH_IN_QBIT="/config/data/nova3/engines/jackett.json"
JACKETT_URL="http://jackett.internal:9117"

print_header "SETTING UP JACKETT/QBITTORRENT SEARCH PLUGIN CONFIG"

# Ensure media services path exists
require_dir "${NEXUS_MEDIA_SERVICES_PATH}" "Media services path"

# Verify qBittorrent container is running
print_step "Checking qBittorrent container status"
if ! docker ps --format '{{.Names}}' | grep -q "^${QBIT_CONTAINER_NAME}$"; then
    print_error "qBittorrent container '${QBIT_CONTAINER_NAME}' is not running"
    print_error "Start it before running this script"
    exit 1
fi
print_success "qBittorrent container is running"

# Verify Jackett container is running (warn only — config can still be written)
if ! docker ps --format '{{.Names}}' | grep -q "^jackett$"; then
    print_warning "Jackett container is not running — config will be written, but searches will fail until it is started"
fi

# Prompt for Jackett API key
print_step "Enter Jackett API key (from the top-right of the Jackett web UI)"
while true; do
    prompt_input "Jackett API key" ""
    JACKETT_API_KEY="${REPLY}"

    if [[ -z "${JACKETT_API_KEY}" ]]; then
        print_warning "API key cannot be empty, please try again"
        continue
    fi

    # Jackett API keys are 32-character alphanumeric strings
    if [[ ! "${JACKETT_API_KEY}" =~ ^[a-zA-Z0-9]{32}$ ]]; then
        print_warning "API key doesn't look like a standard 32-character Jackett key"
        prompt_input "Use it anyway? (y/N)" "n"
        if [[ ! "${REPLY}" =~ ^[Yy]$ ]]; then
            continue
        fi
    fi
    break
done

# Build the JSON config
JACKETT_JSON=$(cat <<EOF
{
    "api_key": "${JACKETT_API_KEY}",
    "url": "${JACKETT_URL}",
    "tracker_first": false,
    "thread_count": 20
}
EOF
)

# Ensure target directory exists inside the container
print_step "Ensuring plugin engines directory exists in qBittorrent container"
if ! docker exec "${QBIT_CONTAINER_NAME}" mkdir -p "$(dirname "${JACKETT_CONFIG_PATH_IN_QBIT}")"; then
    print_error "Failed to create engines directory inside container"
    exit 1
fi

# Write the config file into the container via stdin
print_step "Writing jackett.json into qBittorrent container"
if echo "${JACKETT_JSON}" | docker exec -i "${QBIT_CONTAINER_NAME}" \
    sh -c "cat > '${JACKETT_CONFIG_PATH_IN_QBIT}' && chown 1000:1000 '${JACKETT_CONFIG_PATH_IN_QBIT}' && chmod 644 '${JACKETT_CONFIG_PATH_IN_QBIT}'"; then
    print_success "Wrote ${JACKETT_CONFIG_PATH_IN_QBIT}"
else
    print_error "Failed to write jackett.json to container"
    exit 1
fi

# Verify the file landed correctly
print_step "Verifying configuration"
if docker exec "${QBIT_CONTAINER_NAME}" cat "${JACKETT_CONFIG_PATH_IN_QBIT}" >/dev/null 2>&1; then
    print_success "Configuration file verified in container"
else
    print_error "Could not read back configuration file"
    exit 1
fi

# Test connectivity from qBittorrent container to Jackett
print_step "Testing connectivity from qBittorrent to Jackett"
if docker exec "${QBIT_CONTAINER_NAME}" sh -c "command -v wget >/dev/null && wget -qO- --timeout=5 ${JACKETT_URL} >/dev/null" 2>/dev/null; then
    print_success "qBittorrent can reach Jackett at ${JACKETT_URL}"
elif docker exec "${QBIT_CONTAINER_NAME}" sh -c "command -v curl >/dev/null && curl -sf --max-time 5 ${JACKETT_URL} >/dev/null" 2>/dev/null; then
    print_success "qBittorrent can reach Jackett at ${JACKETT_URL}"
else
    print_warning "Could not verify connectivity to Jackett (wget/curl unavailable, or VPN may be blocking inter-container traffic)"
    print_warning "If searches fail, check that the qBittorrent VPN config allows access to ${JACKETT_URL}"
fi

# Restart qBittorrent so it picks up the new plugin config
#print_step "Restarting qBittorrent container to apply changes"
#if docker restart "${QBIT_CONTAINER_NAME}" >/dev/null; then
#    print_success "qBittorrent restarted"
#else
#    print_error "Failed to restart qBittorrent container"
#    exit 1
#fi

print_info ""
print_info "Next steps:"
print_info "1. Open the qBittorrent WebUI and go to the Search tab"
print_info "2. Click 'Search plugins...' and confirm Jackett is enabled"
print_info "3. Run a test search to verify results come back from Jackett"
