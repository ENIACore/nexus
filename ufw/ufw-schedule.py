#!/bin/bash

source "/etc/nexus/conf/conf.sh"
source "${NEXUS_OPT_DIR}/lib/checks.sh"
source "${NEXUS_OPT_DIR}/lib/print.sh"
source "${NEXUS_OPT_DIR}/lib/log.sh"

print_header "SCHEDULING DAILY UFW BLOCKLIST UPDATE"

NEXUS_UFW_BL_SCRIPT="${NEXUS_ETC_DIR}/ufw/blocklist.sh"
NEXUS_UFW_CRON_SCHEDULE="0 5 * * *"
NEXUS_UFW_CRON_FILE="/etc/cron.d/nexus-ufw-blocklist"

# Ensure nexus user exists
ensure_nexus_user

# Check if cron job already exists
if [[ -f "${NEXUS_UFW_CRON_FILE}" ]]; then
    echo "System cron job already exists at ${NEXUS_UFW_CRON_FILE}"
    exit 1
fi

print_step "Creating system cron job at ${NEXUS_UFW_CRON_FILE}..."

# Create system cron job that runs as nexus user
sudo tee "${NEXUS_UFW_CRON_FILE}" > /dev/null << EOF
# Cloudflare DNS updater - runs as nexus user
# Updates ufw ip blocklist every morning and on reboot

SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Run on boot
@reboot root ${NEXUS_UFW_BL_SCRIPT}

# Run daily - requires root due to commands in blocklist.sh
${NEXUS_UFW_CRON_SCHEDULE} root ${NEXUS_UFW_BL_SCRIPT}
EOF

# Set proper permissions for system cron file
sudo chmod 644 "${NEXUS_UFW_BL_SCRIPT}"
sudo chmod +x "${NEXUS_UFW_BL_SCRIPT}"

print_info "System cron job created successfully"
print_info "UFW blocklist update will run daily as user '${NEXUS_USER}'"
