#!/bin/bash
#Crontab for malicious ip blocking, after firewall setup

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)
SCRIPT_FILE="/opt/firewall.sh"
CRON_SCHEDULE="0 5 * * *"
CRON_FILE="/etc/cron.d/firewall"

# Check if cron job already exists
if [[ -f "${CRON_FILE}" ]]; then
    echo "System cron job already exists at ${CRON_FILE}"
    exit 1
fi

echo "Creating system cron job at ${CRON_FILE}..."

# Create system cron job that runs as root (required for iptables/ipset)
sudo tee "${CRON_FILE}" > /dev/null << EOF
# Firewall IP blocklist updater - runs as root
# Updates malicious IP blocklist daily at 5 AM and on reboot

SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Run on boot
@reboot root ${SCRIPT_FILE}

# Run daily at 5 AM
${CRON_SCHEDULE} root ${SCRIPT_FILE}
EOF

# Set proper permissions for system cron file
sudo chmod 644 "${CRON_FILE}"

echo "System cron job created successfully"
echo "Firewall IP blocklist will update daily at 5 AM as root"
