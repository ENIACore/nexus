#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

NEXUS_UFW_OPT_DIR="${NEXUS_OPT_DIR}/ufw"
NEXUS_UFW_SCRIPT_FILE="${NEXUS_UFW_OPT_DIR}/blocklist.sh"
CRON_SCHEDULE="0 5 * * *"
NEXUS_UFW_CRON_FILE="/etc/cron.d/ufw-blocklist"

print_header "SCHEDULING UFW BLOCKLIST UPDATES"

# Ensure blocklist script exists
require_file "${SCRIPT_FILE}" "UFW blocklist updater script"

# Check if cron job already exists
if [[ -f "${NEXUS_UFW_CRON_FILE}" ]]; then
    print_warning "Cron job already exists at ${NEXUS_UFW_CRON_FILE}"
    print_info "Removing existing cron job and creating new one"
    sudo rm -f "${NEXUS_UFW_CRON_FILE}"
fi

print_step "Creating system cron job at ${NEXUS_UFW_CRON_FILE}"

# Create system cron job that runs as root (required for iptables/ipset)
sudo tee "${NEXUS_UFW_CRON_FILE}" > /dev/null << EOF
# Nexus UFW IP blocklist updater - runs as root
# Updates malicious IP blocklist daily at 5 AM and on reboot

SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Run on boot
@reboot ${NEXUS_USER} ${NEXUS_UFW_SCRIPT_FILE}

# Run daily at 5 AM
${CRON_SCHEDULE} ${NEXUS_USER} ${NEXUS_UFW_SCRIPT_FILE}
EOF

# Set proper permissions for system cron file
print_step "Setting permissions for cron file"
sudo chmod 644 "${NEXUS_UFW_CRON_FILE}"

if [ $? -eq 0 ]; then
    print_success "UFW blocklist cron job scheduled successfully"
    print_info "Blocklist will update daily at 5 AM and on system reboot"
    print_info "Manual updates: ${NEXUS_UFW_OPT_DIR}/update.sh"
else
    print_error "Failed to create cron job"
    exit 1
fi
