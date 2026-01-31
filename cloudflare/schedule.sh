#!/bin/bash

source "/opt/nexus/lib/checks.sh"
source "/etc/nexus/conf/conf.sh"

NEXUS_CF_DNS_SCRIPT="/opt/nexus/cloudflare/update_dns.sh"
NEXUS_CF_CRON_SCHEDULE="*/5 * * * *"
NEXUS_CF_CRON_FILE="/etc/cron.d/nexus-cloudflare-dns"

# Ensure nexus user exists
ensure_nexus_user

# Check if cron job already exists
if [[ -f "${NEXUS_CF_CRON_FILE}" ]]; then
    echo "System cron job already exists at ${NEXUS_CF_CRON_FILE}"
    exit 1
fi

echo "Creating system cron job at ${NEXUS_CF_CRON_FILE}..."

# Create system cron job that runs as nexus user
sudo tee "${NEXUS_CF_CRON_FILE}" > /dev/null << EOF
# Cloudflare DNS updater - runs as nexus user
# Updates DNS records every 5 minutes and on reboot

SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Run on boot
@reboot nexus ${NEXUS_CF_DNS_SCRIPT}

# Run every 5 minutes
${NEXUS_CF_CRON_SCHEDULE} ${NEXUS_USER} ${NEXUS_CF_CRON_SCHEDULE}
EOF

# Set proper permissions for system cron file
sudo chmod 644 "${NEXUS_CF_CRON_FILE}"

echo "System cron job created successfully"
echo "DNS update will run every 5 minutes as user '${NEXUS_USER}'"
