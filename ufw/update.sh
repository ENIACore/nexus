#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_UFW_OPT_DIR="${NEXUS_OPT_DIR}/ufw"
BLOCKLIST_SCRIPT="${NEXUS_UFW_OPT_DIR}/blocklist.sh"

print_header "UPDATING UFW IP BLOCKLIST"

# Ensure blocklist script exists
require_file "${BLOCKLIST_SCRIPT}" "UFW blocklist updater script"

# Run blocklist update
print_step "Running IP blocklist update"
if sudo "${BLOCKLIST_SCRIPT}"; then
    print_success "IP blocklist updated successfully"
else
    print_error "Failed to update IP blocklist"
    exit 1
fi

# Show UFW status
print_step "Current UFW status"
sudo ufw status verbose
