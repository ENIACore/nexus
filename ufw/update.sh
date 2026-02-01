#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_UFW_BL_SCRIPT="${NEXUS_ETC_DIR}/ufw/blocklist.sh"

# Initialize logger
NEXUS_UFW_LOG_DIR="${NEXUS_LOG_DIR}/ufw"
NEXUS_UFW_LOG_FILE="${NEXUS_UFW_LOG_DIR}/ufw.log"
NEXUS_UFW_LOG_MAX_LINES=100
init_logger "${NEXUS_UFW_LOG_FILE}" "${NEXUS_UFW_LOG_MAX_LINES}"

print_header "UPDATING UFW IP BLOCKLIST"

# Ensure blocklist script exists
require_file "${NEXUS_UFW_BL_SCRIPT}" "UFW blocklist updater script"

# Run blocklist update
print_step "Running IP blocklist update"
if sudo "${NEXUS_UFW_BL_SCRIPT}"; then
    log "IP blocklist updated successfully"
else
    log "Failed to update IP blocklist"
    exit 1
fi

# Show UFW status
print_step "Current UFW status"
sudo ufw status verbose
sudo iptables -L INPUT -n -v | head -20
sudo ipset list ipsum | head -20
