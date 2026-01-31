#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

print_header "SETTING UP CLOUDFLARE DNS AND CRON JOB"

NEXUS_CF_OPT_DIR="${NEXUS_OPT_DIR}/cloudflare"
NEXUS_CF_LOG_DIR="${NEXUS_LOG_DIR}/cloudflare"
NEXUS_CF_LOG_FILE="${NEXUS_CF_LOG_DIR}/dns.log"

# Ensure API key is present 
require_file "${NEXUS_ETC_DIR}/keys/cloudflare.sh" "Cloudflare api key file containing NEXUS_CF_API_KEY variable"

# Ensure nexus user exists
ensure_nexus_user

# Set ownership to nexus user so cron job can write logs
sudo chown ${NEXUS_USER}:${NEXUS_USER} "${NEXUS_CF_LOG_DIR}"
sudo chmod 755 "${NEXUS_CF_LOG_DIR}"

print_info "Log directory created successfully"
print_step "Logs will be written to: ${NEXUS_CF_LOG_FILE}"

# Run initial DNS update
print_step "Running initial DNS update..."
source "${NEXUS_CF_OPT_DIR}/update_dns.sh"

if [[ $? -ne 0 ]]; then
    print_error "ERROR: Initial DNS update failed"
    exit 1
fi

# Schedule automated DNS updates
print_step "Scheduling automated DNS updates..."
source "${NEXUS_CF_OPT_DIR}/schedule.sh"

if [[ $? -ne 0 ]]; then
    print_error "ERROR: Failed to schedule DNS updates"
    exit 1
fi

echo "Cloudflare setup complete"
