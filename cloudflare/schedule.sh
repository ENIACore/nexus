#!/bin/bash

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)
USER_FUNCS="${BASE_DIR}/scripts/user_funcs.sh"
SCRIPT_FILE="${BASE_DIR}/cloudflare/update_dns.sh"
CRON_SCHEDULE="*/5 * * * *"
CRON_FILE="/etc/cron.d/cloudflare-dns"

# Check if nexus user exists
source ${USER_FUNCS}
require_nexus_user

# Check if cron job already exists
if [[ -f "${CRON_FILE}" ]]; then
    echo "System cron job already exists at ${CRON_FILE}"
    exit 1
fi

echo "Creating system cron job at ${CRON_FILE}..."

# Create system cron job that runs as nexus user
sudo tee "${CRON_FILE}" > /dev/null << EOF
# Cloudflare DNS updater - runs as nexus user
# Updates DNS records every 5 minutes and on reboot

SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Run on boot
@reboot nexus ${SCRIPT_FILE}

# Run every 5 minutes
${CRON_SCHEDULE} nexus ${SCRIPT_FILE}
EOF

# Set proper permissions for system cron file
sudo chmod 644 "${CRON_FILE}"

echo "System cron job created successfully"
echo "DNS update will run every 5 minutes as user 'nexus'"
