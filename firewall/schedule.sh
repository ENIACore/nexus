#!/bin/bash
#Crontab for malicious ip blocking, after firewall setup

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)
SCRIPT_FILE="/opt/firewall.sh"
CRON_SCHEDULE="0 5 * * *"

if crontab -l 2>/dev/null | grep -q "firewall"; then
    echo "Cron job entry already exists"
    exit 1
fi

(crontab -l 2>/dev/null; echo "@reboot ${SCRIPT_FILE}") | crontab -
(crontab -l 2>/dev/null; echo "${CRON_SCHEDULE} ${SCRIPT_FILE}") | crontab -
